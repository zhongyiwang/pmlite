from flask import current_app
from flask_mail import Message
from threading import Thread
from .init_mail import mail
from typing import List, Optional, Union, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import datetime

# 初始化定时任务调度器（使用后台调度器，不阻塞主线程）
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")  # 设置时区


def init_scheduler(app):
    """在应用初始化是启动调度收起"""
    if not scheduler.running:
        scheduler.start()
        app.logger.info("定时任务调度器已启动")


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
            attachments: Optional[list[tuple]] = None  # 附件格式：[(文件名，内容，MIME类型)， ...]
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
            current_app.logger.error(f"邮件发送错误：{str(e)}", exc_info=True)
            return {"success": False, "message": f"发送失败： {str(e)}"}

    @classmethod
    def send_scheduled_email(
            cls,
            subject: str,
            recipients: List[str],
            html: str,
            trigger: Union[IntervalTrigger, CronTrigger, datetime.datetime],
            sender: Optional[str] = None,
            attachments: Optional[list[tuple]] = None,
            job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        定时发送邮件

        :param subject: 邮件主题
        :param recipients: 收件人列表
        :param html: 邮件内容（html格式）
        :param trigger: 定时触发器
                        - IntervalTrigger：间隔触发（如每30分钟）
                        - CronTrigger： cron表达式触发（如每天8点）
                        - datetime.datetime：指定具体发送时间（一次性）
        :param sender: 发件人，默认使用配置中的MAIL_DEFAULT_SENDER
        :param attachments: 附件列表
        :param job_id: 任务唯一ID（用于后续取消任务）
        :return: 任务信息字典
        """
        try:
            # 验证必要参数
            if not recipients or not subject or not html or not job_id:
                return {"success": False, "message": "缺少必要参数（收件人/主题/内容/job_id）"}

            # 准备邮件参数（避免闭包中引用动态变量）
            app = current_app._get_current_object()
            email_args = {
                "subject": subject,
                "recipients": recipients,
                "html": html,
                "sender": sender or app.config["MAIL_DEFAULT_SENDER"],
                "attachments": attachments
            }

            # 定义定时任务执行的函数
            def scheduled_task():
                # 内部调用发送逻辑，确保在应用上下文中执行
                with app.app_context():
                    msg = Message(
                        subject=email_args["subject"],
                        recipients=email_args["recipients"],
                        sender=email_args["sender"],
                        html=email_args["html"]
                    )
                    if email_args["attachments"]:
                        for filename, content, mimetype in email_args["attachments"]:
                            msg.attach(filename, mimetype, content)
                    cls.send_async_email(app, msg)

            # 添加任务到调度器
            job = scheduler.add_job(
                func=scheduled_task,
                trigger=trigger,
                id=job_id,
                replace_existing=True  # 若job_id已存在，替换它
            )

            # 启动调度器（若未启动）
            if not scheduler.running:
                scheduler.start()
                current_app.logger.info("定时邮件调度器已启动")

            return {
                "success": True,
                "message": "定时邮件任务已添加",
                "job_id": job.id,
                "next_run_time": job.next_run_time
            }

        except Exception as e:
            current_app.logger.error(f"定时邮件任务创建失败：{str(e)}", exc_info=True)
            return {"success": False, "message": f"创建定时任务失败：{str(e)}"}

    @classmethod
    def cancel_scheduled_email(cls, job_id: str) -> Dict[str, str]:
        """取消定时邮件任务"""
        try:
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
                return {"success": True, "message": f"任务 {job_id} 已取消"}
            else:
                return {"success": False, "message": f"任务 {job_id} 不存在"}
        except Exception as e:
            current_app.logger.error(f"取消定时邮件任务失败：{str(e)}", exc_info=True)
            return {"success": False, "message": f"取消任务失败：{str(e)}"}