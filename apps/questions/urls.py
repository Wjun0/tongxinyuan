
from django.urls import path, re_path
from apps.questions import views, channel_views

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

    re_path(r'^submit_check/$', views.SubmitCheckView.as_view()),         # 保存并提交审核  草稿->待审核|已上线（有草稿）->已上线（有草稿待审核）
    re_path(r'^undo_check/$', views.UndoCheckView.as_view()),             # 撤销审核       待审核->草稿
    re_path(r'^submit_check_result/$', views.SubmitCheckResultView.as_view()),  # 审核    待审核->已拒绝|已上线（审核员）
    re_path(r'^operator_online/$', views.OnlineResultView.as_view()),           # 上下线    已上线->已下线| 已下线->草稿（运营人员）
    re_path(r'^delete/$', views.DeleteView.as_view()),      # 删除草稿
    re_path(r'^copy/$', views.CopyAPIView.as_view()),      # 复制问卷


    # 全部问卷列表
    re_path(r'^index/$', views.IndexView.as_view()),            # 问卷列表页
    re_path(r'^show/$', views.ShowquestionAPIView.as_view()),   # 查看问卷
    re_path(r'^used_question/$', views.UsedquestionAPIView.as_view()),   # 查看问卷


    # 频道
    re_path(r'^channel/$', channel_views.ChannelView.as_view()), # 频道列表页
    re_path(r'^add_channel/$', channel_views.ChannelADDView.as_view()), # post新增编辑 / get查看
    re_path(r'^submit_channel/$', channel_views.ChannelSubmitView.as_view()), # 保存提交审核
    re_path(r'^check_channel/$', channel_views.ChannelCheckView.as_view()), # 审核

    # 审批接口
    re_path(r'^check_index/$', views.CheckIndexView.as_view()),  # 审批列表页

]