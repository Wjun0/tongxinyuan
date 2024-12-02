ALTER TABLE tong_question_type_tmp ADD COLUMN qt_type VARCHAR(128);
ALTER TABLE tong_question_type ADD COLUMN qt_type VARCHAR(128);
ALTER TABLE tong_question_tmp ADD COLUMN qt_type VARCHAR(128);
ALTER TABLE tong_question ADD COLUMN qt_type VARCHAR(128);

update tong_question_type set qt_type="文本";
update tong_question_type_tmp set qt_type="文本";
update tong_question set qt_type="文本题";
update tong_question_tmp set qt_type="文本题";

ALTER TABLE `tong-psy`.`tong_user_answer_tmp` 
ADD COLUMN `is_finish` varchar(32) NULL AFTER `result`;