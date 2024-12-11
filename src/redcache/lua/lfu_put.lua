local zset_key = KEYS[1]
local hmap_key = KEYS[2]

local maxsize = tonumber(ARGV[1])
local ttl = ARGV[2]
local hash = ARGV[3]
local retval = ARGV[4]

if maxsize > 0 then
    local n = redis.call('ZCARD', zset_key) - maxsize
    while n >= 0 do
        local popped = redis.call('ZPOPMIN', zset_key)
        redis.call('HDEL', hmap_key, popped[1])
        n = n - 1
    end
end

redis.call('ZINCRBY', zset_key, 1, hash)
redis.call('HSET', hmap_key, hash, retval)

if tonumber(ttl) > 0 then
    redis.call('EXPIRE', zset_key, ttl)
    redis.call('EXPIRE', hmap_key, ttl)
end
redis.call('RPUSH', '__debug__', string.format('<<< put %s', hash))