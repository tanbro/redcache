local zset_key = KEYS[1]
local hmap_key = KEYS[2]

local ttl = ARGV[1]
local hash = ARGV[2]

local rnk = redis.call('ZRANK', zset_key, hash)
local retval = redis.call('HGET', hmap_key, hash)

if rnk ~= nil and retval ~= nil then
    local time = redis.call('TIME')
    redis.call('ZADD', zset_key, time[1] + time[2] / 100000, hash)
elseif rnk == nil and retval ~= nil then
    redis.call('HDEL', hmap_key, hash)
    retval = nil
elseif rnk ~= nil and retval == nil then
    redis.call('ZREM', zset_key, hash)
end

redis.call('EXPIRE', zset_key, ttl)
redis.call('EXPIRE', hmap_key, ttl)

return retval
