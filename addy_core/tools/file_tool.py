"""文件操作工具

提供文件和文件夹的创建、删除、复制、移动、搜索等功能。
"""

import os
import shutil
import glob
from pathlib import Path
from typing import Dict, Any, List
from .base_tool import BaseTool

class FileTool(BaseTool):
    """文件操作工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[FileTool] {x}"))
        
    def get_name(self) -> str:
        return "文件工具"
        
    def get_description(self) -> str:
        return "提供文件和文件夹的创建、删除、复制、移动、搜索等操作"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'create_file',
            'create_folder',
            'delete_file',
            'delete_folder',
            'copy_file',
            'move_file',
            'rename_file',
            'search_files',
            'list_files',
            'read_file',
            'write_file',
            'get_file_info'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行文件操作"""
        try:
            if intent == 'create_file':
                return self._create_file(entities)
            elif intent == 'create_folder':
                return self._create_folder(entities)
            elif intent == 'delete_file':
                return self._delete_file(entities)
            elif intent == 'delete_folder':
                return self._delete_folder(entities)
            elif intent == 'copy_file':
                return self._copy_file(entities)
            elif intent == 'move_file':
                return self._move_file(entities)
            elif intent == 'rename_file':
                return self._rename_file(entities)
            elif intent == 'search_files':
                return self._search_files(entities)
            elif intent == 'list_files':
                return self._list_files(entities)
            elif intent == 'read_file':
                return self._read_file(entities)
            elif intent == 'write_file':
                return self._write_file(entities)
            elif intent == 'get_file_info':
                return self._get_file_info(entities)
            else:
                return f"不支持的文件操作: {intent}"
                
        except Exception as e:
            error_msg = f"文件操作失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _create_file(self, entities: Dict[str, Any]) -> str:
        """创建文件"""
        validation_error = self.validate_entities(['file_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        file_path = entities['file_path']
        content = entities.get('content', '')
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.speak(f"文件已创建: {file_path}")
            return f"file_created: {file_path}"
            
        except Exception as e:
            error_msg = f"创建文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _create_folder(self, entities: Dict[str, Any]) -> str:
        """创建文件夹"""
        validation_error = self.validate_entities(['folder_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        folder_path = entities['folder_path']
        
        try:
            os.makedirs(folder_path, exist_ok=True)
            self.speak(f"文件夹已创建: {folder_path}")
            return f"folder_created: {folder_path}"
            
        except Exception as e:
            error_msg = f"创建文件夹失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _delete_file(self, entities: Dict[str, Any]) -> str:
        """删除文件"""
        validation_error = self.validate_entities(['file_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        file_path = entities['file_path']
        
        if not os.path.exists(file_path):
            self.speak(f"文件不存在: {file_path}")
            return f"error: file_not_found: {file_path}"
            
        try:
            os.remove(file_path)
            self.speak(f"文件已删除: {file_path}")
            return f"file_deleted: {file_path}"
            
        except Exception as e:
            error_msg = f"删除文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _delete_folder(self, entities: Dict[str, Any]) -> str:
        """删除文件夹"""
        validation_error = self.validate_entities(['folder_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        folder_path = entities['folder_path']
        
        if not os.path.exists(folder_path):
            self.speak(f"文件夹不存在: {folder_path}")
            return f"error: folder_not_found: {folder_path}"
            
        try:
            shutil.rmtree(folder_path)
            self.speak(f"文件夹已删除: {folder_path}")
            return f"folder_deleted: {folder_path}"
            
        except Exception as e:
            error_msg = f"删除文件夹失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _copy_file(self, entities: Dict[str, Any]) -> str:
        """复制文件"""
        validation_error = self.validate_entities(['source_path', 'destination_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        source_path = entities['source_path']
        destination_path = entities['destination_path']
        
        if not os.path.exists(source_path):
            self.speak(f"源文件不存在: {source_path}")
            return f"error: source_file_not_found: {source_path}"
            
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copy2(source_path, destination_path)
            self.speak(f"文件已复制: {source_path} -> {destination_path}")
            return f"file_copied: {source_path} -> {destination_path}"
            
        except Exception as e:
            error_msg = f"复制文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _move_file(self, entities: Dict[str, Any]) -> str:
        """移动文件"""
        validation_error = self.validate_entities(['source_path', 'destination_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        source_path = entities['source_path']
        destination_path = entities['destination_path']
        
        if not os.path.exists(source_path):
            self.speak(f"源文件不存在: {source_path}")
            return f"error: source_file_not_found: {source_path}"
            
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.move(source_path, destination_path)
            self.speak(f"文件已移动: {source_path} -> {destination_path}")
            return f"file_moved: {source_path} -> {destination_path}"
            
        except Exception as e:
            error_msg = f"移动文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _rename_file(self, entities: Dict[str, Any]) -> str:
        """重命名文件"""
        validation_error = self.validate_entities(['old_name', 'new_name'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        old_name = entities['old_name']
        new_name = entities['new_name']
        
        if not os.path.exists(old_name):
            self.speak(f"文件不存在: {old_name}")
            return f"error: file_not_found: {old_name}"
            
        try:
            os.rename(old_name, new_name)
            self.speak(f"文件已重命名: {old_name} -> {new_name}")
            return f"file_renamed: {old_name} -> {new_name}"
            
        except Exception as e:
            error_msg = f"重命名文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _search_files(self, entities: Dict[str, Any]) -> str:
        """搜索文件"""
        validation_error = self.validate_entities(['pattern'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        pattern = entities['pattern']
        search_path = entities.get('search_path', '.')
        
        try:
            # 使用glob进行文件搜索
            search_pattern = os.path.join(search_path, '**', pattern)
            files = glob.glob(search_pattern, recursive=True)
            
            if files:
                files_list = '\n'.join(files[:10])  # 限制显示前10个结果
                if len(files) > 10:
                    files_list += f"\n... 还有 {len(files) - 10} 个文件"
                self.speak(f"找到 {len(files)} 个匹配的文件:\n{files_list}")
                return f"files_found: {len(files)}"
            else:
                self.speak(f"未找到匹配模式 '{pattern}' 的文件")
                return "no_files_found"
                
        except Exception as e:
            error_msg = f"搜索文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _list_files(self, entities: Dict[str, Any]) -> str:
        """列出文件"""
        directory = entities.get('directory', '.')
        
        if not os.path.exists(directory):
            self.speak(f"目录不存在: {directory}")
            return f"error: directory_not_found: {directory}"
            
        try:
            items = os.listdir(directory)
            files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
            folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
            
            result = f"目录 {directory} 包含:\n"
            if folders:
                result += f"文件夹 ({len(folders)}): {', '.join(folders[:5])}"
                if len(folders) > 5:
                    result += f" ... 还有 {len(folders) - 5} 个"
                result += "\n"
            if files:
                result += f"文件 ({len(files)}): {', '.join(files[:5])}"
                if len(files) > 5:
                    result += f" ... 还有 {len(files) - 5} 个"
                    
            self.speak(result)
            return f"directory_listed: {len(files)} files, {len(folders)} folders"
            
        except Exception as e:
            error_msg = f"列出文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _read_file(self, entities: Dict[str, Any]) -> str:
        """读取文件内容"""
        validation_error = self.validate_entities(['file_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        file_path = entities['file_path']
        max_length = entities.get('max_length', 500)  # 限制读取长度
        
        if not os.path.exists(file_path):
            self.speak(f"文件不存在: {file_path}")
            return f"error: file_not_found: {file_path}"
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_length)
                if len(content) == max_length:
                    content += "... (内容已截断)"
                    
            self.speak(f"文件内容:\n{content}")
            return f"file_read: {file_path}"
            
        except Exception as e:
            error_msg = f"读取文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _write_file(self, entities: Dict[str, Any]) -> str:
        """写入文件内容"""
        validation_error = self.validate_entities(['file_path', 'content'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        file_path = entities['file_path']
        content = entities['content']
        append_mode = entities.get('append', False)
        
        try:
            mode = 'a' if append_mode else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
                
            action = "追加到" if append_mode else "写入"
            self.speak(f"内容已{action}文件: {file_path}")
            return f"file_written: {file_path}"
            
        except Exception as e:
            error_msg = f"写入文件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_file_info(self, entities: Dict[str, Any]) -> str:
        """获取文件信息"""
        validation_error = self.validate_entities(['file_path'], entities)
        if validation_error:
            self.speak(validation_error)
            return f"error: {validation_error}"
            
        file_path = entities['file_path']
        
        if not os.path.exists(file_path):
            self.speak(f"文件不存在: {file_path}")
            return f"error: file_not_found: {file_path}"
            
        try:
            stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            info = f"文件信息:\n"
            info += f"名称: {path_obj.name}\n"
            info += f"大小: {stat.st_size} 字节\n"
            info += f"类型: {'文件夹' if path_obj.is_dir() else '文件'}\n"
            info += f"修改时间: {stat.st_mtime}\n"
            
            self.speak(info)
            return f"file_info_retrieved: {file_path}"
            
        except Exception as e:
            error_msg = f"获取文件信息失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"