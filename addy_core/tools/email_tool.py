"""邮件工具

提供邮件发送、接收、管理等功能。
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_tool import BaseTool

class EmailTool(BaseTool):
    """邮件工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[EmailTool] {x}"))
        
        # 邮件配置
        self.smtp_server = None
        self.smtp_port = None
        self.imap_server = None
        self.imap_port = None
        self.email_address = None
        self.email_password = None
        
        if config:
            self.smtp_server = config.get('Email', 'smtp_server', fallback=None)
            self.smtp_port = config.getint('Email', 'smtp_port', fallback=587)
            self.imap_server = config.get('Email', 'imap_server', fallback=None)
            self.imap_port = config.getint('Email', 'imap_port', fallback=993)
            self.email_address = config.get('Email', 'email_address', fallback=None)
            self.email_password = config.get('Email', 'email_password', fallback=None)
        
    def get_name(self) -> str:
        return "邮件工具"
        
    def get_description(self) -> str:
        return "提供邮件发送、接收、管理等功能"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'send_email',
            'read_emails',
            'search_emails',
            'delete_email',
            'mark_email_read',
            'mark_email_unread',
            'get_email_count',
            'send_email_with_attachment',
            'get_unread_emails',
            'reply_email',
            'forward_email',
            'create_email_draft'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行邮件操作"""
        try:
            if intent == 'send_email':
                return self._send_email(entities)
            elif intent == 'read_emails':
                return self._read_emails(entities)
            elif intent == 'search_emails':
                return self._search_emails(entities)
            elif intent == 'delete_email':
                return self._delete_email(entities)
            elif intent == 'mark_email_read':
                return self._mark_email_read(entities)
            elif intent == 'mark_email_unread':
                return self._mark_email_unread(entities)
            elif intent == 'get_email_count':
                return self._get_email_count(entities)
            elif intent == 'send_email_with_attachment':
                return self._send_email_with_attachment(entities)
            elif intent == 'get_unread_emails':
                return self._get_unread_emails(entities)
            elif intent == 'reply_email':
                return self._reply_email(entities)
            elif intent == 'forward_email':
                return self._forward_email(entities)
            elif intent == 'create_email_draft':
                return self._create_email_draft(entities)
            else:
                return f"不支持的邮件操作: {intent}"
                
        except Exception as e:
            error_msg = f"邮件操作失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _check_email_config(self) -> bool:
        """检查邮件配置是否完整"""
        if not all([self.email_address, self.email_password]):
            self.speak("请在配置文件中设置邮件账户和密码")
            return False
        return True
        
    def _send_email(self, entities: Dict[str, Any]) -> str:
        """发送邮件"""
        if not self._check_email_config():
            return "error: missing_email_config"
            
        to_email = entities.get('to_email')
        subject = entities.get('subject', '无主题')
        body = entities.get('body', '')
        cc_emails = entities.get('cc_emails', [])
        bcc_emails = entities.get('bcc_emails', [])
        
        if not to_email:
            self.speak("请提供收件人邮箱地址")
            return "error: missing_recipient"
            
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email if isinstance(to_email, str) else ', '.join(to_email)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            if bcc_emails:
                msg['Bcc'] = ', '.join(bcc_emails)
                
            # 添加邮件正文
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                
                # 准备收件人列表
                recipients = []
                if isinstance(to_email, str):
                    recipients.append(to_email)
                else:
                    recipients.extend(to_email)
                recipients.extend(cc_emails)
                recipients.extend(bcc_emails)
                
                server.send_message(msg, to_addrs=recipients)
                
            success_msg = f"邮件已发送给 {to_email}"
            self.speak(success_msg)
            return f"email_sent: {to_email}"
            
        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _send_email_with_attachment(self, entities: Dict[str, Any]) -> str:
        """发送带附件的邮件"""
        if not self._check_email_config():
            return "error: missing_email_config"
            
        to_email = entities.get('to_email')
        subject = entities.get('subject', '无主题')
        body = entities.get('body', '')
        attachment_path = entities.get('attachment_path')
        
        if not to_email:
            self.speak("请提供收件人邮箱地址")
            return "error: missing_recipient"
            
        if not attachment_path or not os.path.exists(attachment_path):
            self.speak("请提供有效的附件路径")
            return "error: invalid_attachment_path"
            
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}'
            )
            msg.attach(part)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
                
            success_msg = f"带附件的邮件已发送给 {to_email}"
            self.speak(success_msg)
            return f"email_with_attachment_sent: {to_email}"
            
        except Exception as e:
            error_msg = f"发送带附件邮件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _read_emails(self, entities: Dict[str, Any]) -> str:
        """读取邮件"""
        if not self._check_email_config():
            return "error: missing_email_config"
            
        folder = entities.get('folder', 'INBOX')
        count = entities.get('count', 5)
        
        try:
            # 连接IMAP服务器
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as mail:
                mail.login(self.email_address, self.email_password)
                mail.select(folder)
                
                # 搜索邮件
                status, messages = mail.search(None, 'ALL')
                if status != 'OK':
                    self.speak("搜索邮件失败")
                    return "error: search_failed"
                    
                message_ids = messages[0].split()
                
                if not message_ids:
                    self.speak(f"{folder}文件夹中没有邮件")
                    return "no_emails_found"
                    
                # 获取最新的几封邮件
                latest_ids = message_ids[-count:]
                emails_info = []
                
                for msg_id in reversed(latest_ids):
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # 解析邮件信息
                        subject = self._decode_header(email_message['Subject'])
                        sender = self._decode_header(email_message['From'])
                        date = email_message['Date']
                        
                        emails_info.append({
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'id': msg_id.decode()
                        })
                        
                # 格式化邮件信息
                if emails_info:
                    info = f"最新{len(emails_info)}封邮件:\n"
                    for i, email_info in enumerate(emails_info, 1):
                        info += f"{i}. 主题: {email_info['subject']}\n"
                        info += f"   发件人: {email_info['sender']}\n"
                        info += f"   日期: {email_info['date']}\n\n"
                        
                    self.speak(info)
                    return f"emails_read: {len(emails_info)}"
                else:
                    self.speak("没有找到邮件")
                    return "no_emails_found"
                    
        except Exception as e:
            error_msg = f"读取邮件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_unread_emails(self, entities: Dict[str, Any]) -> str:
        """获取未读邮件"""
        if not self._check_email_config():
            return "error: missing_email_config"
            
        folder = entities.get('folder', 'INBOX')
        
        try:
            # 连接IMAP服务器
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as mail:
                mail.login(self.email_address, self.email_password)
                mail.select(folder)
                
                # 搜索未读邮件
                status, messages = mail.search(None, 'UNSEEN')
                if status != 'OK':
                    self.speak("搜索未读邮件失败")
                    return "error: search_failed"
                    
                message_ids = messages[0].split()
                
                if not message_ids:
                    self.speak("没有未读邮件")
                    return "no_unread_emails"
                    
                unread_emails = []
                
                for msg_id in reversed(message_ids[-10:]):  # 最多显示10封
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject = self._decode_header(email_message['Subject'])
                        sender = self._decode_header(email_message['From'])
                        date = email_message['Date']
                        
                        unread_emails.append({
                            'subject': subject,
                            'sender': sender,
                            'date': date
                        })
                        
                if unread_emails:
                    info = f"您有{len(message_ids)}封未读邮件，最新的{len(unread_emails)}封:\n"
                    for i, email_info in enumerate(unread_emails, 1):
                        info += f"{i}. {email_info['subject']} - {email_info['sender']}\n"
                        
                    self.speak(info)
                    return f"unread_emails_found: {len(message_ids)}"
                    
        except Exception as e:
            error_msg = f"获取未读邮件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _search_emails(self, entities: Dict[str, Any]) -> str:
        """搜索邮件"""
        if not self._check_email_config():
            return "error: missing_email_config"
            
        keyword = entities.get('keyword')
        sender = entities.get('sender')
        subject = entities.get('subject')
        folder = entities.get('folder', 'INBOX')
        
        if not any([keyword, sender, subject]):
            self.speak("请提供搜索关键词、发件人或主题")
            return "error: missing_search_criteria"
            
        try:
            # 连接IMAP服务器
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as mail:
                mail.login(self.email_address, self.email_password)
                mail.select(folder)
                
                # 构建搜索条件
                search_criteria = []
                if sender:
                    search_criteria.append(f'FROM "{sender}"')
                if subject:
                    search_criteria.append(f'SUBJECT "{subject}"')
                if keyword:
                    search_criteria.append(f'TEXT "{keyword}"')
                    
                search_string = ' '.join(search_criteria)
                
                # 执行搜索
                status, messages = mail.search(None, search_string)
                if status != 'OK':
                    self.speak("搜索邮件失败")
                    return "error: search_failed"
                    
                message_ids = messages[0].split()
                
                if not message_ids:
                    self.speak("没有找到匹配的邮件")
                    return "no_emails_found"
                    
                # 获取搜索结果
                found_emails = []
                for msg_id in reversed(message_ids[-10:]):  # 最多显示10封
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        subject_text = self._decode_header(email_message['Subject'])
                        sender_text = self._decode_header(email_message['From'])
                        date = email_message['Date']
                        
                        found_emails.append({
                            'subject': subject_text,
                            'sender': sender_text,
                            'date': date
                        })
                        
                if found_emails:
                    info = f"找到{len(message_ids)}封匹配邮件，显示最新{len(found_emails)}封:\n"
                    for i, email_info in enumerate(found_emails, 1):
                        info += f"{i}. {email_info['subject']} - {email_info['sender']}\n"
                        
                    self.speak(info)
                    return f"emails_found: {len(message_ids)}"
                    
        except Exception as e:
            error_msg = f"搜索邮件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_email_count(self, entities: Dict[str, Any]) -> str:
        """获取邮件数量"""
        if not self._check_email_config():
            return "error: missing_email_config"
            
        folder = entities.get('folder', 'INBOX')
        
        try:
            # 连接IMAP服务器
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as mail:
                mail.login(self.email_address, self.email_password)
                mail.select(folder)
                
                # 获取总邮件数
                status, total_messages = mail.search(None, 'ALL')
                total_count = len(total_messages[0].split()) if total_messages[0] else 0
                
                # 获取未读邮件数
                status, unread_messages = mail.search(None, 'UNSEEN')
                unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
                
                info = f"{folder}文件夹邮件统计:\n"
                info += f"总邮件数: {total_count}\n"
                info += f"未读邮件数: {unread_count}\n"
                info += f"已读邮件数: {total_count - unread_count}\n"
                
                self.speak(info)
                return f"email_count_retrieved: total={total_count}, unread={unread_count}"
                
        except Exception as e:
            error_msg = f"获取邮件数量失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _create_email_draft(self, entities: Dict[str, Any]) -> str:
        """创建邮件草稿"""
        to_email = entities.get('to_email')
        subject = entities.get('subject', '草稿')
        body = entities.get('body', '')
        
        if not to_email:
            self.speak("请提供收件人邮箱地址")
            return "error: missing_recipient"
            
        # 创建草稿文件
        draft_filename = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        draft_path = os.path.join(os.getcwd(), 'drafts', draft_filename)
        
        # 确保草稿目录存在
        os.makedirs(os.path.dirname(draft_path), exist_ok=True)
        
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(f"收件人: {to_email}\n")
                f.write(f"主题: {subject}\n")
                f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n正文:\n")
                f.write(body)
                
            success_msg = f"邮件草稿已保存到 {draft_path}"
            self.speak(success_msg)
            return f"email_draft_created: {draft_filename}"
            
        except Exception as e:
            error_msg = f"创建邮件草稿失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _decode_header(self, header_value):
        """解码邮件头部信息"""
        if header_value is None:
            return "无"
            
        try:
            decoded_header = email.header.decode_header(header_value)
            decoded_string = ""
            
            for part, encoding in decoded_header:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
                    
            return decoded_string
        except Exception:
            return str(header_value)
            
    def _mark_email_read(self, entities: Dict[str, Any]) -> str:
        """标记邮件为已读"""
        # 这个功能需要邮件ID，在实际实现中需要更复杂的邮件管理
        self.speak("标记邮件已读功能需要具体的邮件ID")
        return "feature_requires_email_id"
        
    def _mark_email_unread(self, entities: Dict[str, Any]) -> str:
        """标记邮件为未读"""
        # 这个功能需要邮件ID，在实际实现中需要更复杂的邮件管理
        self.speak("标记邮件未读功能需要具体的邮件ID")
        return "feature_requires_email_id"
        
    def _delete_email(self, entities: Dict[str, Any]) -> str:
        """删除邮件"""
        # 这个功能需要邮件ID，在实际实现中需要更复杂的邮件管理
        self.speak("删除邮件功能需要具体的邮件ID")
        return "feature_requires_email_id"
        
    def _reply_email(self, entities: Dict[str, Any]) -> str:
        """回复邮件"""
        # 这个功能需要原邮件信息，在实际实现中需要更复杂的邮件管理
        self.speak("回复邮件功能需要原邮件的详细信息")
        return "feature_requires_original_email"
        
    def _forward_email(self, entities: Dict[str, Any]) -> str:
        """转发邮件"""
        # 这个功能需要原邮件信息，在实际实现中需要更复杂的邮件管理
        self.speak("转发邮件功能需要原邮件的详细信息")
        return "feature_requires_original_email"