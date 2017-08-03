require 'uri'
require 'net/http'
require 'json'
require_relative '../../API/methods/test_data'

class General
  def get_uid
    url = URI("#{TestData[:url_serv]}:7079/api/v1/getuid")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Get.new(url)
    response = http.request(request)
    @cookie = response.response['set-cookie']
    body = response.read_body
    parse_uid = JSON.parse(body)
    parse_uid["uid"]
  end

  def get_sign(forsign)
    url = URI("#{TestData[:url_serv]}:7079/api/v1/signtest/")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Post.new(url)
    request['Cookie'] = @cookie
    request.body = "forsign=#{forsign}&private=#{TestData[:private_key]}"
    response = http.request(request)
    body = response.read_body
    parse_body = JSON.parse(body)
    @pubkey = parse_body["pubkey"]
    @signature = parse_body["signature"]
  end

  def login
    url = URI("#{TestData[:url_serv]}:7079/api/v1/login")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Post.new(url)
    request['Cookie'] = @cookie
    request.body = "pubkey=#{@pubkey}&signature=#{@signature}&state=#{TestData[:state]}"
    response = http.request(request)
    body = response.read_body
    parse_address = JSON.parse(body)
    @address = parse_address["address"]
  end

  def balance
    url = URI("#{TestData[:url_serv]}:7079/api/v1/balance/#{@address}")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Get.new(url)
    request['Cookie'] = @cookie
    response = http.request(request)
    response.read_body
  end

  def prepare
    url = URI("#{TestData[:url_serv]}:7079/api/v1/prepare/sendegs")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Post.new(url)
    request['Cookie'] = @cookie
    request.body = "pubkey=#{@pubkey}&recipient=#{TestData[:recipient]}&amount=#{TestData[:amount]}&commission=#{TestData[:commission]}&comment=qwe"
    response = http.request(request)
    body = response.read_body
    parse_forsign = JSON.parse(body)
    @time = parse_forsign["time"]
    @forsign = parse_forsign["forsign"]
  end

  def sendegs
    url = URI("#{TestData[:url_serv]}:7079/api/v1/sendegs")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Post.new(url)
    request['Cookie'] = @cookie
    request.body = "pubkey=#{@pubkey}&recipient=#{TestData[:recipient]}&amount=#{TestData[:amount]}&commission=#{TestData[:commission]}&comment=qwe&signature=#{@signature}&time=#{@time}"
    response = http.request(request)
    body = response.read_body
    parse_hash = JSON.parse(body)
    @hash = parse_hash["hash"]
  end

  def txstatus
    url = URI("#{TestData[:url_serv]}:7079/api/v1/txstatus/#{@hash}")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Get.new(url)
    request['Cookie'] = @cookie
    response = http.request(request)
    response.read_body
  end
end