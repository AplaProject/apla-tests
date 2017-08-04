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
    sign_params = "forsign=#{forsign}&private=#{TestData[:private_key]}"
    body = post_req("#{TestData[:url_serv]}signtest/", sign_params)
    parse_body = JSON.parse(body)
    @pubkey = parse_body["pubkey"]
    @signature = parse_body["signature"]
  end

  def login
    login = "pubkey=#{@pubkey}&signature=#{@signature}&state=#{TestData[:state]}"
    body = post_req("#{TestData[:url_serv]}login", login)
    parse_address = JSON.parse(body)
    @address = parse_address["address"]
  end

  def balance
    get_req("#{TestData[:url_serv]}balance/#{@address}")
  end

  def prepare
    prepare = "pubkey=#{@pubkey}&recipient=#{TestData[:recipient]}&amount=#{TestData[:amount]}&commission=#{TestData[:commission]}&comment=qwe"
    body = post_req("#{TestData[:url_serv]}prepare/sendegs", prepare)
    parse_forsign = JSON.parse(body)
    @time = parse_forsign["time"]
    @forsign = parse_forsign["forsign"]
  end

  def sendegs
    sendegs_params = "pubkey=#{@pubkey}&recipient=#{TestData[:recipient]}&amount=#{TestData[:amount]}&commission=#{TestData[:commission]}&comment=qwe&signature=#{@signature}&time=#{@time}"
    body = post_req("#{TestData[:url_serv]}sendegs", sendegs_params)
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

  def post_req(url, params)
    url = URI(url)
    http = Net::HTTP.new(url.host, url.port)
    request = Net::HTTP::Post.new(url)
    request['Cookie'] = @cookie
    request.body = params
    response = http.request(request)
    response.read_body
  end

end