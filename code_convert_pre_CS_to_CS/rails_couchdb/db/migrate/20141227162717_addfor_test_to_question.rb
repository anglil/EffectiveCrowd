class AddforTestToQuestion < ActiveRecord::Migration
  def change
  	add_column :question, :for_test, :string
  end
end
