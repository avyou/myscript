-- HTTP access auth
-- by avyou
-- at 20150923
--

ip_deny_time = 600 --10 min
ip_time_out  = 30  -- 30 sec
connect_count = 15  -- 30 frequency
cookie_expire = 3600 --1 hours


function auth()
    local red = redis_connect()
    if not red then
        return false
    end
    lqtk = red:get(ngx.var.cookie_lqtk) or nil
    if ngx.var.cookie_lqtk ~= nil and ngx.var.cookie_lqtk == lqtk then
       return
    else
        local username = ngx.var.remote_user
        local password = ngx.var.remote_passwd
        if auth_user(username, password) then
            local lqtk = ngx.md5(ngx.var.remote_addr..os.time()..math.random(1000000000,10000000000))
            local expires = cookie_expire  -- 1 hours
            ngx.header["Set-Cookie"] = "lqtk="..lqtk..";Domain=.5usport.com; Path=/; Expires=" .. ngx.cookie_time(ngx.time() + expires)
            red:set(lqtk,lqtk)
            red:expire(lqtk,lqtk,cookie_expire)
            redis_close(red)
            return
        end
        access_deny(red)
        ngx.header.www_authenticate = [[Basic realm="access auth"]]
        ngx.exit(401)
    end
end

function redis_connect()
   local redis_info = {
        host="192.168.xxx.xxx",
        port=6379,
        db=9,
        password='xxxx'
    }
    local redis = require "resty.redis"
    local red = redis:new()
    red:set_timeout(3000) -- 3 sec

    local ok, err = red:connect(redis_info["host"], redis_info["port"])
    if not ok then
        return false
    end

    local ok, err = red:auth(redis_info["password"])
    if not ok then
        return false
    end

    local ok, err = red:select(redis_info["db"])
    if not ok then
       return false
    end
    return red
end

function redis_close(red)  
    if not red then  
        return 
    end  
    local ok, err = red:close()  
    if not ok then  
        return false
    end  
end  

function auth_user(username,password)
    local red = redis_connect()
    if not red then
        return false
    end
    local res, err = red:hmget(username, "username", "password")
    if res and res ~= ngx.null then
        local user = res[1] or ""
        local pass = res[2] or ""
        local keyString = "liaoqiu-5usport-com"
        local password = ngx.md5(password..keyString)
        if user ~="" and pass ~= "" and  username == user and password == pass then
            --ngx.say("username: " .. user .. " , redis query password: " .. pass)
            redis_close(red)
            return true
        end
    else
        return false
    end
end


function access_deny(red)
    local red = redis_connect()
    if not red then
        return false
    end

    local is_deny,err=red:get("access:deny:"..ngx.var.remote_addr)

    if is_deny == '1' then
        ngx.exit(403)
    end

    local start_time,err = red:get("access:time:"..ngx.var.remote_addr)
    local ip_count,err = red:get("access:count:"..ngx.var.remote_addr)

    if start_time == ngx.null or os.time() - start_time > ip_time_out then
        red:set("access:time:"..ngx.var.remote_addr,os.time())
        red:set("access:count:"..ngx.var.remote_addr,1)
    else
        ip_count = ip_count + 1
        red:incr("access:count:"..ngx.var.remote_addr)
        if ip_count >= connect_count then
            red:set("access:deny:"..ngx.var.remote_addr,1)
            red:expire("access:deny:"..ngx.var.remote_addr,ip_deny_time)
        end
    end
    redis_close(red)
end

if ngx.var.remote_addr ~= '1.1.1.1' then
    auth()
end
