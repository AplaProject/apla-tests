require 'uri'
require 'net/http'
require 'json'
require_relative '../../API/methods/test_data'

class ApiV1
  def get_uid
    url = URI("#{TestData[:url_serv]}getuid")
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Get.new(url)
    response = http.request(request)
    @cookie = response.response['set-cookie'].split('; ')[0]
    body = response.read_body
    parse_uid = JSON.parse(body)
    parse_uid["uid"]
  end

  def get_sign(forsign)
    url = URI("#{TestData[:url_serv]}signtest/")
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
    url = URI("#{TestData[:url_serv]}login")
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
    get_req("#{TestData[:url_serv]}balance/#{@address}")
  end

  def prepare
    url = URI("#{TestData[:url_serv]}prepare/sendegs")
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
    url = URI("#{TestData[:url_serv]}sendegs")
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
    get_req("#{TestData[:url_serv]}txstatus/#{@hash}")
  end


  private

  def get_req(url)
    url = URI(url)
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Get.new(url)
    request['Cookie'] = @cookie
    response = http.request(request)
    response.read_body
  end

end