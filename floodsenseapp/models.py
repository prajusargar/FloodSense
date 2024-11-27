from django.db import models

# Create your models here.


class SensorData(models.Model):
    s_id = models.AutoField(primary_key=True)

    nodename = models.CharField(max_length=255)
    latitude  = models.TextField(default="")
    longitude = models.TextField(default="")

    monsoonintensity = models.TextField(default="")
    topographydrainage = models.TextField(default="")
    rivermanagement = models.TextField(default="")
    climatechange = models.TextField(default="")
    siltation = models.TextField(default="")
    drainagesystems = models.TextField(default="")
    coastalvulnerability = models.TextField(default="")
    watersheds = models.TextField(default="")
    deterioratinginfrastructure = models.TextField(default="")
    wetlandloss = models.TextField(default="")

    predicttime = models.TextField(default="")
    predictionclass = models.TextField(default="")
    predictprobability = models.TextField(default="")

    timestamp = models.DateTimeField(auto_now_add=True)

    # mode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.s_id} - {self.nodename} - {self.predicttime} - {self.predictionclass} - {self.predictprobability} - {self.timestamp}"


class AlertNotifyData(models.Model):
    s_id = models.AutoField(primary_key=True)

    nodename = models.CharField(max_length=255, default="India")

    msgRecipients = models.TextField(default="no recipients")
    msg = models.TextField(default="no message")

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nodename} - {self.msgRecipients} - {self.timestamp} - {self.msg}"




class ImgData(models.Model):
  img_id = models.AutoField(primary_key=True)

  nodename = models.CharField(max_length=255)

  imgBase64Text = models.CharField(max_length=255)

  timestamp = models.DateTimeField(auto_now_add=True)

  # mode = models.CharField(max_length=10)

  def __str__(self):
      return f"""{self.img_id} - {self.timestamp}"""



class FeedBackData(models.Model):
  feed_id = models.AutoField(primary_key=True)

  topic         = models.TextField()
  username      = models.CharField(max_length=255)

  MsgText       = models.TextField()

  timestamp     = models.DateTimeField(auto_now_add=True)

  # mode = models.CharField(max_length=10)

  def __str__(self):
      return f"""{self.feed_id} - User:{self.username} - 
      TimeStamp{self.timestamp} - Topic:{self.topic}  """


class ReportedFloodAlertData(models.Model):
  report_id = models.AutoField(primary_key=True)

  topic         = models.TextField()
  username      = models.CharField(max_length=255)
  location      = models.CharField(max_length=255)

  MsgText       = models.TextField()

  timestamp     = models.DateTimeField(auto_now_add=True)

  # mode = models.CharField(max_length=10)

  def __str__(self):
      return f"""{self.report_id} - User:{self.username} - 
      TimeStamp{self.timestamp} - Topic:{self.topic}  """

class ChatData(models.Model):
  chat_id = models.AutoField(primary_key=True)

  username      = models.CharField(max_length=255)
  role          = models.CharField(max_length=255, default="none")

  ChatText      = models.TextField()

  timestamp     = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"""{self.chat_id} - User:{self.username} - 
      TimeStamp{self.timestamp} - Topic:{self.ChatText}  """



class FaqData(models.Model):
  faq_id = models.AutoField(primary_key=True)

  Question      = models.TextField()
  Answer      = models.TextField()


  def __str__(self):
      return f"""{self.faq_id} - {self.Question} - {self.Answer}"""