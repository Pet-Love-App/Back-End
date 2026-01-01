import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { randomString, randomIntBetween, randomEmail } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';
import { Trend, Counter, Rate } from 'k6/metrics';

// ========== 1. 核心配置（支持多环境/多压力模型） ==========
const SUPABASE_URL = __ENV.SUPABASE_URL || 'https://nbneznvuvbpgqqkgsanr.supabase.co';
const SERVICE_ROLE = __ENV.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ibmV6bnZ1dmJwZ3Fxa2dzYW5yIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDgxMzM1NCwiZXhwIjoyMDgwMzg5MzU0fQ.lKFtLjPgjld4NaPERukYmnuI6rtL22Kcfu-1rqLomfY';
if (!SERVICE_ROLE) throw new Error('SUPABASE_SERVICE_ROLE_KEY is required');

const TEST_MODE = __ENV.TEST_MODE || 'spike';
const BASE_VUS = Number(__ENV.K6_BASE_VUS) || 10;
const PEAK_VUS = Number(__ENV.K6_PEAK_VUS) || 50;
const TEST_DURATION = __ENV.K6_DURATION || '5m';
const SPIKE_DURATION = __ENV.SPIKE_DURATION || '30s';
const STEP_DURATION = __ENV.STEP_DURATION || '2m';
const POOL_SIZE = Math.max(Number(__ENV.K6_POOL_SIZE) || 20, BASE_VUS * 2);

const AUTH_ADMIN_BASE = `${SUPABASE_URL.replace(/\/$/, '')}/auth/v1/admin`;
const REST_BASE = `${SUPABASE_URL.replace(/\/$/, '')}/rest/v1`;
const baseHeaders = {
  'Content-Type': 'application/json',
  Accept: 'application/json',
  apikey: SERVICE_ROLE,
  Authorization: `Bearer ${SERVICE_ROLE}`,
  'X-Client-Type': 'k6-load-test',
};

// writeHeaders: for write operations, force PostgREST to return representation
const writeHeaders = (extra = {}) => Object.assign({}, baseHeaders, { Prefer: 'return=representation' }, extra);

// ========== 2. 自定义性能指标 ==========
const postCreateTrend = new Trend('post_create_duration', true);
const postListTrend = new Trend('post_list_duration', true);
const friendReqTrend = new Trend('friend_req_duration', true);
const userCreateTrend = new Trend('user_create_duration', true);
const profileUpdateTrend = new Trend('profile_update_duration', true);

const postCreateCounter = new Counter('post_create_total');
const friendReqCounter = new Counter('friend_req_total');
const profileUpdateCounter = new Counter('profile_update_total');
const totalErrors = new Counter('total_errors');
const expectedConflicts = new Counter('expected_conflicts');

const postCreateSuccessRate = new Rate('post_create_success');
const friendReqSuccessRate = new Rate('friend_req_success');
const userCreateSuccessRate = new Rate('user_create_success');
const profileUpdateSuccessRate = new Rate('profile_update_success');

const post400Errors = new Counter('post_400_errors');
const friend409Errors = new Counter('friend_409_errors');
const profile400Errors = new Counter('profile_400_errors');
const profile409Errors = new Counter('profile_409_errors');

// ========== 3. 工具函数 ==========
// 从用户池中选择下一个接收者 ID（避免返回 callerId）
// 策略：优先轮询 + 随机退避，保证高并发下不会总选到相同目标。
// 参数 poolIds: Array of user UUIDs
// 返回：一个不同于 callerId 的 userId，若无法找到返回 null
function getNextReceiverId(callerId, poolIds) {
  if (!Array.isArray(poolIds) || poolIds.length === 0) return null;

  // 如果池内仅有 callerId，则没有接收者
  if (poolIds.length === 1 && poolIds[0] === callerId) return null;

  // 尝试按 VU 或时间做伪轮询：使用当前 timestamp + random 来挑选不同索引
  const now = Date.now();
  const baseIndex = (now % poolIds.length);
  // 试几个位置，直到找到不是 callerId 的 id
  for (let i = 0; i < Math.min(poolIds.length, 10); i++) {
    const idx = (baseIndex + i + Math.floor(Math.random() * 3)) % poolIds.length;
    const candidate = poolIds[idx];
    if (candidate && candidate !== callerId) return candidate;
  }

  // 最后尝试随机选一个不是 callerId
  for (let i = 0; i < 5; i++) {
    const candidate = poolIds[Math.floor(Math.random() * poolIds.length)];
    if (candidate && candidate !== callerId) return candidate;
  }

  return null;
}

function toPostgresArray(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return '{}';
  const escaped = arr.map(item => {
    const str = String(item).replace(/"/g, '\\"').replace(/,/g, '\\,').replace(/{/g, '\\{').replace(/}/g, '\\}');
    return str;
  });
  return `{${escaped.join(',')}}`;
}

function buildUrl(baseUrl, params = {}) {
  const entries = Object.entries(params)
    .filter(([_, v]) => v !== undefined && v !== null)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`);
  if (entries.length === 0) return baseUrl;
  return `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}${entries.join('&')}`;
}

// ---------- Low-cardinality helpers (NEW) ----------
function normalizeUrlForMetrics(url, method = '') {
  if (!url) return 'unknown_request';
  try {
    const u = new URL(url, 'http://example'); // base for relative urls
    let path = u.pathname
      .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/ig, ':id')
      .replace(/\/\d+(?=\/|$)/g, '/:id')
      .replace(/\/[A-Za-z0-9_-]{10,}/g, '/:token')
      .replace(/\/{2,}/g, '/');

    if (path === '') path = '/';
    return method ? `${method.toUpperCase()} ${path}` : `${path}`;
  } catch (err) {
    return 'unknown_request';
  }
}

function idToBucket(id, buckets = 100) {
  if (!id) return 'bucket_unknown';
  let h = 0;
  for (let i = 0; i < id.length; i++) {
    h = ((h << 5) - h) + id.charCodeAt(i);
    h |= 0;
  }
  const idx = Math.abs(h) % Math.max(1, buckets);
  return `bucket_${idx}`;
}

function buildLowCardinalityTags(url, method, extraTags = {}) {
  const name = normalizeUrlForMetrics(url, method);
  const tags = Object.assign({}, extraTags, { name });
  return tags;
}
// ---------- End low-cardinality helpers ----------

function restRequest(method, url, data = null, headers = baseHeaders, retry = 1, scene = '') {
  let res;
  const start = Date.now();
  let isExpectedConflict = false;

  // Inject low-cardinality name tag automatically
  const tags = buildLowCardinalityTags(url, method);

  for (let i = 0; i <= retry; i++) {
    try {
      res = http.request(method, url, data ? JSON.stringify(data) : null, {
        headers,
        timeout: 10000,
        tags, // ensure k6 uses tags.name (low-cardinality) instead of full URL
      });
    } catch (e) {
      totalErrors.add(1);
      if (i === retry) throw e;
      sleep(0.5 + Math.random());
      continue;
    }

    if (res.status >= 500 && res.status < 600 && i < retry) {
      totalErrors.add(1);
      sleep(0.5 + Math.random());
      continue;
    }

    if (res.status === 409) {
      if (url.includes('/rest/v1/profiles')) {
        isExpectedConflict = true;
        expectedConflicts.add(1);
        profile409Errors.add(1);
      } else if (url.includes('/rest/v1/friend_requests')) {
        isExpectedConflict = true;
        expectedConflicts.add(1);
        friend409Errors.add(1);
      }
    }

    if (res.status === 400) {
      if (url.includes('/rest/v1/posts')) {
        post400Errors.add(1);
        console.error(`[POST 400] 帖子创建 - 请求体：${JSON.stringify(data)}，响应：${res.body}`);
      } else if (url.includes('/rest/v1/profiles')) {
        profile400Errors.add(1);
        console.error(`[${method} 400] Profile操作 - ID: ${data?.id || url.match(/eq\.([0-9a-f-]+)/)?.[1] || 'unknown'}, 请求体：${JSON.stringify(data)}，响应：${res.body}`);
      }
    }

    break;
  }

  const duration = Date.now() - start;
  let parsed = null;
  try {
    const body = res.body || '';
    if (body && body.trim().length) parsed = JSON.parse(body);
  } catch (e) {
    parsed = null;
    if (!isExpectedConflict) totalErrors.add(1);
  }

  const allowedStatus = [200, 201, 204, 409];
  if (res && res.status >= 400 && !isExpectedConflict && !allowedStatus.includes(res.status)) {
    totalErrors.add(1);
  }

  return {
    status: res && res.status ? Number(res.status) : null,
    body: res ? res.body : null,
    parsed,
    url,
    duration,
    isExpectedConflict
  };
}

function restV1(method, path, data = null, queryParams = {}, headers = baseHeaders, retry = 1, scene = '') {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  const url = buildUrl(`${REST_BASE}/${cleanPath}`, queryParams);
  return restRequest(method, url, data, headers, retry, scene);
}

// extract id from POST/INSERT response (array/object)
function extractIdFromResponse(res) {
  if (!res) return null;
  if (res.parsed) {
    if (Array.isArray(res.parsed)) return res.parsed[0]?.id || null;
    if (typeof res.parsed === 'object') return res.parsed.id || null;
  }
  return null;
}

// fallback: query recent posts by author to find likely inserted id (best-effort)
function fallbackFindPostIdByAuthor(callerId) {
  const recent = restV1('GET', 'posts', null, {
    select: 'id,created_at',
    author_id: `eq.${callerId}`,
    order: 'created_at.desc',
    limit: 5
  }, baseHeaders, 1);

  if (recent && recent.parsed && Array.isArray(recent.parsed) && recent.parsed.length > 0) {
    return recent.parsed[0].id;
  }
  return null;
}

// check if friend request or friends relationship already exists (both directions)
function checkFriendExists(userA, userB) {
  const q1 = restV1('GET', 'friend_requests', null, {
    select: 'id',
    sender_id: `eq.${userA}`,
    receiver_id: `eq.${userB}`,
    status: `in.(pending,accepted)`
  }, baseHeaders, 1);
  if (q1 && q1.parsed && Array.isArray(q1.parsed) && q1.parsed.length > 0) return true;

  const q2 = restV1('GET', 'friend_requests', null, {
    select: 'id',
    sender_id: `eq.${userB}`,
    receiver_id: `eq.${userA}`,
    status: `in.(pending,accepted)`
  }, baseHeaders, 1);
  if (q2 && q2.parsed && Array.isArray(q2.parsed) && q2.parsed.length > 0) return true;

  const f1 = restV1('GET', 'friends', null, {
    select: 'id',
    user_id: `eq.${userA}`,
    friend_id: `eq.${userB}`
  }, baseHeaders, 1);
  if (f1 && f1.parsed && Array.isArray(f1.parsed) && f1.parsed.length > 0) return true;

  const f2 = restV1('GET', 'friends', null, {
    select: 'id',
    user_id: `eq.${userB}`,
    friend_id: `eq.${userA}`
  }, baseHeaders, 1);
  if (f2 && f2.parsed && Array.isArray(f2.parsed) && f2.parsed.length > 0) return true;

  return false;
}

// safe POST that returns id or does fallback
function safePostWithIdFallback(path, payload, callerId, scene) {
  const res = restV1('POST', path, payload, {}, writeHeaders(), 2, scene);
  const id = extractIdFromResponse(res);
  if (id) return { res, id };
  const fallbackId = fallbackFindPostIdByAuthor(callerId);
  if (fallbackId) return { res, id: fallbackId };
  return { res, id: null };
}

// ========== 4. CRUD helpers (auth/profile) ==========
function createAuthUser(email, password) {
  const url = `${AUTH_ADMIN_BASE}/users`;
  const payload = {
    email,
    password,
    email_confirm: true,
    user_metadata: { created_by: 'k6_perf_test' }
  };
  const start = Date.now();
  const res = restRequest('POST', url, payload, baseHeaders, 2);
  userCreateTrend.add(Date.now() - start);
  userCreateSuccessRate.add([200, 201, 409].includes(res.status));
  return res;
}

function deleteAuthUser(userId) {
  const url = `${AUTH_ADMIN_BASE}/users/${encodeURIComponent(userId)}`;
  return restRequest('DELETE', url, null, baseHeaders, 1);
}

function ensureProfileExists(profileId, payload) {
  const headers = Object.assign({}, baseHeaders, { Prefer: 'return=representation' });
  const allowedFields = ['id', 'username', 'avatar_url', 'bio', 'created_at', 'updated_at'];
  const cleanPayload = Object.keys(payload)
    .filter(key => allowedFields.includes(key))
    .reduce((obj, key) => { obj[key] = payload[key]; return obj; }, {});
  if (cleanPayload.username && !cleanPayload.username.includes(Date.now().toString())) {
    cleanPayload.username = `${cleanPayload.username}_${Date.now()}_${randomIntBetween(1000, 9999)}`;
  }

  const patchRes = restV1('PATCH', `profiles`, cleanPayload, { id: `eq.${profileId}` }, headers, 1, 'profile');
  if ([200, 204].includes(patchRes.status)) {
    profileUpdateTrend.add(patchRes.duration);
    profileUpdateCounter.add(1);
    profileUpdateSuccessRate.add(true);
    return patchRes;
  }

  if (patchRes.status === 404) {
    const postPayload = Object.assign({ id: profileId }, cleanPayload);
    const postRes = restV1('POST', 'profiles', postPayload, {}, headers, 2, 'profile');
    if ([200, 201, 409].includes(postRes.status)) {
      profileUpdateTrend.add(postRes.duration);
      profileUpdateCounter.add(1);
      profileUpdateSuccessRate.add(true);
      return postRes;
    }
  }

  totalErrors.add(1);
  profileUpdateSuccessRate.add(false);
  profileUpdateTrend.add(patchRes.duration);
  profileUpdateCounter.add(1);
  return patchRes;
}

// data generators
function generateValidPostData(callerId, vu) {
  // reduce per-request uniqueness in tags: remove timestamp/random in tags array
  const tag = `k6_vu${vu}`;
  const tagsArray = [`k6`, `perf`, `test`, `vu${vu}`];
  return {
    content: `Performance test post: ${tag} - ${randomString(20)}`,
    category: ['pet', 'food', 'care'][randomIntBetween(0, 2)],
    created_at: new Date().toISOString(),
    author_id: callerId,
    tags: toPostgresArray(tagsArray)
  };
}

function generateUniqueFriendRequest(senderId, receiverId, vu) {
  const reqId = `${Date.now()}_${randomIntBetween(1000, 9999)}`;
  return {
    sender_id: senderId,
    receiver_id: receiverId,
    status: 'pending',
    message: `Perf test friend req (VU${vu}): ${randomString(8)}`,
    created_at: new Date().toISOString()
  };
}

function generateValidProfileData(vu) {
  const newAvatar = `https://via.placeholder.com/${randomIntBetween(200, 500)}`;
  return {
    avatar_url: newAvatar,
    updated_at: new Date().toISOString(),
    bio: `Performance test bio (VU${vu}): ${randomString(40)}`
  };
}

// ========== 5. 压力模型配置 ==========
export const options = {
  ...(TEST_MODE === 'stress' && {
    stages: [
      { duration: '1m', target: BASE_VUS },
      { duration: '2m', target: PEAK_VUS/2 },
      { duration: '2m', target: PEAK_VUS },
      { duration: '3m', target: Math.floor(PEAK_VUS*1.5) },
      { duration: '2m', target: PEAK_VUS },
      { duration: '1m', target: 0 },
    ],
  }),
  ...(TEST_MODE === 'load' && {
    stages: [
      { duration: '1m', target: BASE_VUS },
      { duration: TEST_DURATION, target: BASE_VUS },
      { duration: '1m', target: 0 },
    ],
  }),
  ...(TEST_MODE === 'soak' && {
    stages: [
      { duration: '10m', target: Math.floor(BASE_VUS/2) },
      { duration: '8h', target: Math.floor(BASE_VUS/2) },
      { duration: '10m', target: 0 },
    ],
  }),
  ...(TEST_MODE === 'spike' && {
    stages: [
      { duration: '1m', target: 10 },
      { duration: '10s', target: PEAK_VUS },
      { duration: SPIKE_DURATION, target: PEAK_VUS },
      { duration: '10s', target: 10 },
      { duration: '2m', target: 0 },
    ],
  }),
  ...(TEST_MODE === 'step' && {
    stages: Array.from({ length: 5 }).map((_, i) => ({
      duration: STEP_DURATION,
      target: BASE_VUS + (i * 10),
    })).concat([{ duration: '1m', target: 0 }]),
  }),

  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<2000'],
    post_create_duration: ['p(95)<1500'],
    friend_req_duration: ['p(95)<1000'],
    profile_update_duration: ['p(95)<800'],
    post_create_success: ['rate>0.98'],
    friend_req_success: ['rate>0.98'],
    user_create_success: ['rate>0.98'],
    profile_update_success: ['rate>0.99'],
    total_errors: ['count<50'],
  },

  discardResponseBodies: false,
  userAgent: 'k6-supabase-performance-test/1.0',
  ext: {
    loadimpact: {
      name: `Supabase ${TEST_MODE.toUpperCase()} Test (${new Date().toISOString()})`,
    },
  },
};

// ========== 6. 全局变量 ==========
let globalPool = { ids: [], created: false };
const vuContext = {};

// ========== 7. 预热数据池 ==========
export function setup() {
  console.log(`===== 开始预热用户池（${POOL_SIZE}个用户）- ${TEST_MODE.toUpperCase()}测试 =====`);
  try {
    restV1('DELETE', 'profiles', null, { username: `like.k6_%` }, baseHeaders, 1);
    restV1('DELETE', 'posts', null, { content: `like.*Performance test post*` }, baseHeaders, 1);
    restV1('DELETE', 'friend_requests', null, { message: `like.*Perf test friend req*` }, baseHeaders, 1);
  } catch (e) {
    console.warn('清理残留数据时发生错误:', e.message);
  }

  const validPoolIds = [];
  for (let i = 0; i < POOL_SIZE; i++) {
    try {
      const ts = Date.now();
      const randomSuffix = randomIntBetween(10000, 99999);
      const email = `k6+pool-${i}-${ts}-${randomSuffix}@example.com`;
      const pw = `k6pool!${randomString(12)}`;

      const userRes = createAuthUser(email, pw);
      if ([200, 201, 409].includes(userRes.status) && userRes.parsed && userRes.parsed.id) {
        const userId = userRes.parsed.id;

        const profilePayload = {
          username: `k6_pool_${i}_${ts}_${randomSuffix}`,
          created_at: new Date().toISOString(),
          avatar_url: `https://via.placeholder.com/${randomIntBetween(100, 300)}`,
          bio: `Pool user ${i} (created at ${new Date().toISOString()})`
        };
        const profileRes = ensureProfileExists(userId, profilePayload);
        if ([200, 201, 204, 409].includes(profileRes.status)) {
          validPoolIds.push(userId);
          console.log(`预热用户 ${i+1}/${POOL_SIZE} 创建成功：${userId}`);
        } else {
          totalErrors.add(1);
          console.error(`预热用户 ${i+1} Profile创建失败：`, profileRes.status, profileRes.parsed || profileRes.body);
        }
      } else {
        totalErrors.add(1);
        console.error(`预热用户 ${i+1} Auth创建失败：`, userRes.status, userRes.parsed || userRes.body);
      }
    } catch (e) {
      totalErrors.add(1);
      console.error(`创建预热用户 ${i+1} 时发生异常：`, e.message);
    }

    sleep(0.1);
  }

  globalPool.ids = validPoolIds;
  globalPool.created = true;

  console.log(`===== 预热完成，创建/复用了 ${globalPool.ids.length} 个有效用户 =====`);
  return { pool: globalPool };
}

// ========== 8. 核心测试逻辑 ==========
export default function (data) {
  const { pool } = data;
  const vu = __VU;

  if (!pool || !pool.ids || pool.ids.length === 0) {
    console.error(`VU${vu} 预热池为空，无法执行测试`);
    sleep(1 + Math.random() * 2);
    return;
  }

  if (!vuContext[vu]) {
    vuContext[vu] = {
      userId: null,
      posts: [],
      friendRequests: [],
      lastAction: Date.now()
    };
  }

  if (!vuContext[vu].userId) {
    try {
      const ts = Date.now();
      const randomSuffix = randomIntBetween(10000, 99999);
      const email = `k6+vu${vu}-${ts}-${randomSuffix}@example.com`;
      const pw = `k6vu!${randomString(12)}`;

      const userRes = createAuthUser(email, pw);
      if ([200, 201, 409].includes(userRes.status) && userRes.parsed && userRes.parsed.id) {
        vuContext[vu].userId = userRes.parsed.id;

        ensureProfileExists(userRes.parsed.id, {
          username: `k6_vu_${vu}_${ts}_${randomSuffix}`,
          created_at: new Date().toISOString(),
          avatar_url: `https://via.placeholder.com/${randomIntBetween(100, 300)}`
        });

        console.log(`VU${vu} 专属用户创建成功：${userRes.parsed.id}`);
      } else {
        vuContext[vu].userId = pool.ids[Math.floor(Math.random() * pool.ids.length)];
        console.log(`VU${vu} 用户创建失败，降级使用预热池用户：${vuContext[vu].userId}`);
      }
    } catch (e) {
      vuContext[vu].userId = pool.ids[Math.floor(Math.random() * pool.ids.length)];
      console.error(`VU${vu} 创建用户时异常，降级使用预热池用户：`, e.message);
    }
  }

  const callerId = vuContext[vu].userId;
  if (!callerId) {
    sleep(1 + Math.random() * 2);
    return;
  }

  const r = Math.random();

  if (r < 0.4) {
    group('📖 帖子列表查询', () => {
      const categories = ['pet', 'food', 'care'];
      const category = categories[randomIntBetween(0, categories.length - 1)];
      const start = Date.now();

      const res = restV1('GET', 'posts', null, {
        select: 'id,author_id,content,category,created_at,tags',
        category: `eq.${category}`,
        limit: randomIntBetween(5, 20),
        order: 'created_at.desc'
      }, baseHeaders, 1);

      postListTrend.add(Date.now() - start);

      check(res, {
        '帖子列表返回200': (x) => x.status === 200,
        '帖子列表非空': (x) => x.parsed && Array.isArray(x.parsed) && x.parsed.length > 0,
        '无服务端错误': (x) => !x.isExpectedConflict && x.status < 500,
      });
    });
  } else if (r < 0.7) {
    group('✍️ 创建帖子', () => {
      const postPayload = generateValidPostData(callerId, vu);
      const start = Date.now();

      // use safePostWithIdFallback
      const { res: postRes, id: postId } = safePostWithIdFallback('posts', postPayload, callerId, 'post');

      postCreateTrend.add(Date.now() - start);
      postCreateCounter.add(1);
      postCreateSuccessRate.add([200, 201].includes(postRes.status));

      const postIdExists = !!postId;
      check(postRes, {
        '创建帖子成功': (x) => [200, 201].includes(x.status),
        '帖子ID返回或回退成功': () => postIdExists,
        '无服务端错误': (x) => !x.isExpectedConflict && x.status < 500,
      });

      if (postIdExists) {
        vuContext[vu].posts.push(postId);
      } else {
        totalErrors.add(1);
        console.error('无法获取帖子 id', postRes.status, postRes.body);
      }
    });
  } else if (r < 0.9) {
    group('🤝 发送好友请求', () => {
      const receiverId = getNextReceiverId(callerId, pool.ids);
      if (!receiverId) {
        console.error(`VU${vu} 接收方ID为空，无法发送好友请求`);
        friendReqSuccessRate.add(false);
        return;
      }

      // 检查是否已存在 friend_requests 或 friends（双向）
      const already = checkFriendExists(callerId, receiverId);
      if (already) {
        expectedConflicts.add(1);
        friendReqSuccessRate.add(true);
        return;
      }

      // 轻微随机延迟减小 race window
      sleep(Math.random() * 0.05);

      const friendPayload = generateUniqueFriendRequest(callerId, receiverId, vu);
      const { res: friendRes, id: friendId } = safePostWithIdFallback('friend_requests', friendPayload, callerId, 'friend');

      friendReqTrend.add(friendRes.duration);
      friendReqCounter.add(1);
      friendReqSuccessRate.add([200, 201, 409].includes(friendRes.status));

      check(friendRes, {
        '创建好友请求成功/已存在': (x) => [200, 201, 409].includes(x.status),
        '无服务端错误': (x) => !x.isExpectedConflict && x.status < 500,
      });

      if (friendId) {
        vuContext[vu].friendRequests.push(friendId);
      } else {
        if (friendRes && friendRes.status === 409) {
          expectedConflicts.add(1);
          friendReqSuccessRate.add(true);
        } else {
          totalErrors.add(1);
          console.error('好友请求未返回 id 且无回退', friendRes.status, friendRes.body);
        }
      }
    });
  } else {
    group('👤 更新个人资料', () => {
      const profilePayload = generateValidProfileData(vu);
      const start = Date.now();
      const res = ensureProfileExists(callerId, profilePayload);

      profileUpdateTrend.add(res.duration);
      profileUpdateCounter.add(1);
      profileUpdateSuccessRate.add([200, 204, 409].includes(res.status));

      check(res, {
        '更新资料成功/已存在': (x) => [200, 204, 409].includes(x.status),
        '无服务端错误': (x) => !x.isExpectedConflict && x.status < 500,
      });
    });
  }

  const thinkTime = randomIntBetween(500, 3000);
  sleep(thinkTime / 1000);
}

// ========== 9. 清理逻辑 ==========
export function teardown(data) {
  console.log(`===== 开始清理测试数据（${new Date().toISOString()}）=====`);

  console.log(`===== 测试错误统计 =====`);
  console.log(`帖子400错误数：${post400Errors.value}`);
  console.log(`Profile400错误数：${profile400Errors.value}`);
  console.log(`好友请求409错误数：${friend409Errors.value}`);
  console.log(`Profile409错误数：${profile409Errors.value}`);
  console.log(`总错误数：${totalErrors.value}`);
  console.log(`预期冲突数：${expectedConflicts.value}`);

  const vuKeys = Object.keys(vuContext);
  console.log(`清理 ${vuKeys.length} 个VU的测试数据...`);

  for (const vu of vuKeys) {
    try {
      const ctx = vuContext[vu];
      if (!ctx) continue;

      if (ctx.posts && ctx.posts.length > 0) {
        const ids = ctx.posts.join(',');
        const delPosts = restV1('DELETE', 'posts', null, { id: `in.(${ids})` }, baseHeaders, 1);
        console.log(`VU${vu} 删除 ${ctx.posts.length} 个帖子：${delPosts.status}`);
      }

      if (ctx.friendRequests && ctx.friendRequests.length > 0) {
        const ids = ctx.friendRequests.join(',');
        const delFriend = restV1('DELETE', 'friend_requests', null, { id: `in.(${ids})` }, baseHeaders, 1);
        console.log(`VU${vu} 删除 ${ctx.friendRequests.length} 个好友请求：${delFriend.status}`);
      }

      if (ctx.userId) {
        const delProfile = restV1('DELETE', 'profiles', null, { id: `eq.${ctx.userId}` }, baseHeaders, 1);
        const delAuth = deleteAuthUser(ctx.userId);
        console.log(`VU${vu} 删除用户 ${ctx.userId}：Profile(${delProfile.status}) / Auth(${delAuth.status})`);
      }
    } catch (e) {
      console.error(`清理VU${vu}数据时发生错误：`, e.message);
    }
  }

  try {
    if (data.pool && data.pool.ids && data.pool.ids.length > 0) {
      console.log(`清理 ${data.pool.ids.length} 个预热池用户...`);
      const poolIds = data.pool.ids.join(',');
      restV1('DELETE', 'profiles', null, { id: `in.(${poolIds})` }, baseHeaders, 1);
      for (const pid of data.pool.ids) {
        deleteAuthUser(pid);
        sleep(0.01);
      }
    }
  } catch (e) {
    console.error('清理预热池数据时发生错误：', e.message);
  }

  try {
    console.log('模糊清理残留测试数据...');
    restV1('DELETE', 'friend_requests', null, { message: `like.*Perf test friend req*` }, baseHeaders, 1);
    restV1('DELETE', 'posts', null, { content: `like.*Performance test post*` }, baseHeaders, 1);
    restV1('DELETE', 'profiles', null, { username: `like.k6_%` }, baseHeaders, 1);
  } catch (e) {
    console.error('模糊清理残留数据时发生错误：', e.message);
  }

  console.log(`===== 数据清理完成（${new Date().toISOString()}）=====`);
}
