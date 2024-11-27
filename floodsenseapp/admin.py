from django.contrib import admin

from .models import SensorData, AlertNotifyData, ImgData, ChatData, FeedBackData, ReportedFloodAlertData, FaqData

# # Register your models here.

admin.site.register(SensorData)
admin.site.register(AlertNotifyData)
admin.site.register(ImgData)
admin.site.register(ChatData)
admin.site.register(FeedBackData)
admin.site.register(ReportedFloodAlertData)
admin.site.register(FaqData)