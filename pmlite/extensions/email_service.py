from flask import current_app
from flask_mail import Message
from threading import Thread
from .init_mail import mail
from typing import List, Optional

class EmailService:
    """基于Flask-Mail的邮件服务类，支持异步发送"""

    @classmethod
    def send_async_email(cls, app, msg):
        """异步发送邮件（避免阻塞请求）"""
        with app.app_context():
            try:
                mail.send(msg)
                current_app.logger.info(f"邮件发送成功：主题={msg.subject}， 收件人={msg.recipients}")
            except Exception as e:
                current_app.logger.error(f"邮件发送失败：{str(e)}", exc_info=True)

    @classmethod
    def send_email(
            cls,
            subject: str,
            recipients: List[str],
            html: str,
            sender: Optional[str] = None,
            attachments: Optional[list[tuple]] = None # 附件格式：[(文件名，内容，MIME类型)， ...]
    ) -> dict:
        """
        发送邮件

        :param subject:邮件主题
        :param recipients: 收件人列表
        :param html: 邮件内容（html格式）
        :param sender: 发件人，默认使用配置中的MAIL_DEFAULT_SENDER
        :param attachments: 附件列表
        :return: 发送结果字典
        """
        try:
            # 验证必要参数
            if not recipients or not subject or not html:
                return {"success": False, "message": "缺少必要参数（收件人/主题/内容）"}

            # 创建邮件详细
            msg = Message(
                subject=subject,
                recipients=recipients,
                sender=sender or current_app.config["MAIL_DEFAULT_SENDER"],
                html=html
            )

            # 添加附件
            if attachments:
                for filename, content, mimetype in attachments:
                    msg.attach(filename, mimetype, content)

            # 异步发送邮件
            Thread(
                target=cls.send_async_email,
                args=(current_app._get_current_object(), msg)  # 使用实际应用实例
            ).start()

            return {"success": True, "message": "邮件已加入发送队列"}

        except Exception as e:
            current_app.loger.error(f"邮件发送错误：{str(e)}", exc_info=True)
            return {"success": False, "message": f"发送失败： {str(e)}"}
