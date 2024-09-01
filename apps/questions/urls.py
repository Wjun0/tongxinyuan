
from django.urls import path, re_path
from apps.questions import views

urlpatterns = [
    re_path(r'^add_question_type/$', views.ADDQuestionsTypeView.as_view()), # 添加问题类型（第一步）
    re_path(r'^add_question/$', views.ADDQuestionsView.as_view()),          # 添加问题和选项 （第二步）
    re_path(r'^get_option_data/$', views.GetOptionView.as_view()),          # 获取问卷和选项个数
    re_path(r'^get_options/$', views.GetOptionsView.as_view()),             # 获取问题下的选项个数
    re_path(r'^add_order_value/$', views.ADDOrderAndValueView.as_view()),   # 录入分值 （第三步）
    re_path(r'^get_questions/$', views.GetquestionsView.as_view()),         # 获取题号和选项值
    re_path(r'^add_calculate/$', views.ADDCalculateView.as_view()),        # 添加因子（第三步） | 获取因子结果
    re_path(r'^add_result/$', views.ADDResultView.as_view()),              # 添加不同维度结果 （第四步）
    re_path(r'^show_result/$', views.ShowResultView.as_view()),            # 预览结果 tmp表结果
    # re_path(r'^get_option_value/$', views.GetOptionValueView.as_view()),

    re_path(r'^submit_check/$', views.SubmitCheckView.as_view()),         # 保存并提交审核  草稿->待审核|已上线（有草稿）->待审核
    re_path(r'^undo_check/$', views.UndoCheckView.as_view()),             # 撤销审核       待审核->草稿
    re_path(r'^submit_check_result/$', views.SubmitCheckResultView.as_view()),  # 审核    待审核->已拒绝|已上线（审核员）
    re_path(r'^operator_online/$', views.OnlineResultView.as_view()),           # 上下线    已上线->已下线| 已下线->草稿（运营人员）







    # 查询接口
    re_path(r'^index/$', views.IndexView.as_view()),
]