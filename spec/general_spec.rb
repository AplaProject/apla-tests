require 'rspec'
require 'uri'
require 'net/http'
require 'json'
require_relative '../../API/methods/general'
require_relative '../../API/methods/test_data'

describe 'Test General API' do

  test = nil

  before(:all) do
    test = General.new
  end

  it 'getuid' do
    expect(test.get_uid).to match(/[0-9]/)
  end

  it 'login' do
    test.get_sign(test.get_uid)
    wallet = test.login
    expect(wallet).to match(/[0-9]/)
  end

  it 'balance' do
    balance = test.balance
    expect(JSON.parse(balance)["amount"]).to match(/[0-9]/)
    expect(JSON.parse(balance)["egs"]).to match(/[0-9]/)
  end

  it 'sendegs' do
    test.prepare
    test.get_sign(test.prepare)
    test.sendegs
  end

  it 'txstatus' do
    test.txstatus
    sleep 3
    test.txstatus
    expect(JSON.parse(test.txstatus)["blockid"]).to match(/[0-9]/)
  end
end