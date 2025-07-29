import requests

class EmailService:
    API_URL = 'http://172.28.130.96:8030/ZHD.ashx?option=2'

    @classmethod
    def send_email(cls, subject, recipients, html, sender_name="项目管理平台PMS"):
        """
        发送邮件
        :param subject: 邮件主题
        :param recipients: 收件人，列表
        :param html: 邮件内容
        :param sender_name: 发件人名称
        """
        headers = {
            "Content-Type": "application/json"
        }

        try:
            payload = {
                "subject": subject,
                "recipients": recipients,
                "html": html,
                "sender_name": sender_name
            }

            response = requests.post(
                cls.API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )

            response_data = response.json()

            print(response_data)

        except Exception as e:
            print('错误',e)