require 'test_helper'

class MturkControllerTest < ActionController::TestCase
  test "should get complete" do
    get :complete
    assert_response :success
  end

  test "should get login" do
    get :login
    assert_response :success
  end

  test "should get tutorialPage1" do
    get :tutorialPage1
    assert_response :success
  end

  test "should get tutorialPage2" do
    get :tutorialPage2
    assert_response :success
  end

  test "should get consentPage" do
    get :consentPage
    assert_response :success
  end

  test "should get question" do
    get :question
    assert_response :success
  end

end
