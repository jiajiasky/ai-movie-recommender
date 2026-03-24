/**
 * 飞书多维表格 API 代理服务
 * 用于前端网页读写影评数据
 * 
 * 使用方式：
 * 1. 本地运行: node server.js
 * 2. 部署到 Vercel/Netlify: 按平台配置
 */

const http = require('http');
const https = require('https');

// ========== 配置 ==========
const APP_TOKEN = 'TyyVbBgbAaVBxDsAvfKc5S6UnRe';
const TABLE_ID = 'tbl1P0ElQM82WxQU';

// 飞书 API 地址
const FEISHU_API = 'open.feishu.cn';
const BATCH_CREATE_URL = '/bitable/v1/apps/TyyVbBgbAaVBxDsAvfKc5S6UnRe/tables/tbl1P0ElQM82WxQU/records';
const BATCH_GET_URL = '/bitable/v1/apps/TyyVbBgbAaVBxDsAvfKc5S6UnRe/tables/tbl1P0ElQM82WxQU/records';

// 内部token（需要替换为实际的 tenant_access_token）
// 获取方式：https://open.feishu.cn/document/server-docs/getting-started-4/register-and-create-an-internal-app
let TENANT_ACCESS_TOKEN = '';

// ========== API 函数 ==========

/**
 * 获取 tenant_access_token
 */
async function getTenantToken() {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({
            app_id: 'cli_xxxxxxxxxxxx',  // 替换为你的 app_id
            app_secret: 'xxxxxxxxxxxx'  // 替换为你的 app_secret
        });

        const options = {
            hostname: FEISHU_API,
            path: '/open-apis/auth/v3/tenant_access_token/internal',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    if (result.code === 0) {
                        resolve(result.tenant_access_token);
                    } else {
                        reject(new Error(result.msg));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

/**
 * 从飞书获取所有影评
 */
async function getReviews(movieName) {
    const token = await getTenantToken();
    
    return new Promise((resolve, reject) => {
        const options = {
            hostname: FEISHU_API,
            path: `${BATCH_GET_URL}?filter=contains(field_id_contains("电影名称"), "${encodeURIComponent(movieName)}")`,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    if (result.code === 0) {
                        // 转换格式
                        const reviews = result.data.items.map(item => ({
                            movie: item.fields['电影名称'],
                            username: item.fields['用户昵称'],
                            rating: item.fields['评分'],
                            review: item.fields['影评内容'],
                            date: item.fields['发布时间']
                        }));
                        resolve(reviews);
                    } else {
                        reject(new Error(result.msg));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', reject);
        req.end();
    });
}

/**
 * 提交影评到飞书
 */
async function addReview(reviewData) {
    const token = await getTenantToken();
    
    // 字段 ID 映射
    const fields = {
        '电影名称': reviewData.movie,
        '用户昵称': reviewData.username,
        '评分': parseFloat(reviewData.rating),
        '影评内容': reviewData.review,
        '发布时间': Date.now()  // 毫秒时间戳
    };

    const postData = JSON.stringify({ fields });

    return new Promise((resolve, reject) => {
        const options = {
            hostname: FEISHU_API,
            path: BATCH_CREATE_URL,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    if (result.code === 0) {
                        resolve({ success: true, record_id: result.data.record_id });
                    } else {
                        reject(new Error(result.msg));
                    }
                } catch (e) {
                    reject(e);
                }
            });
        });

        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// ========== HTTP 服务器 ==========

const server = http.createServer(async (req, res) => {
    // 设置 CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // 解析 URL
    const url = new URL(req.url, `http://${req.headers.host}`);
    const path = url.pathname;
    const method = req.method;

    try {
        if (path === '/api/reviews' && method === 'GET') {
            // 获取影评列表
            const movieName = url.searchParams.get('movie') || '';
            const reviews = await getReviews(movieName);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, data: reviews }));
            return;
        }

        if (path === '/api/reviews' && method === 'POST') {
            // 提交影评
            let body = '';
            req.on('data', chunk => body += chunk);
            req.on('end', async () => {
                const reviewData = JSON.parse(body);
                const result = await addReview(reviewData);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
            });
            return;
        }

        // 404
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'Not found' }));

    } catch (error) {
        console.error('Error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
    }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`
📋 API Endpoints:
   GET  /api/reviews?movie=电影名   - 获取影评列表
   POST /api/reviews                - 提交影评

📝 Request Body:
   {
     "movie": "肖申克的救赎",
     "username": "小明", 
     "rating": 9.5,
     "review": "影评内容..."
   }
    `);
});
