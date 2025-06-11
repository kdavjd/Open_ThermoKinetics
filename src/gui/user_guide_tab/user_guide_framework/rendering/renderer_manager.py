"""
Renderer Manager - Менеджер системы рендеринга контента
"""

from typing import Any, Dict, List, Optional

from PyQt6.QtWidgets import QLabel, QWidget

from src.core.logger_config import LoggerManager
from src.core.state_logger import StateLogger
from src.gui.user_guide_tab.user_guide_framework.rendering.renderers import (
    BaseRenderer,
    CodeRenderer,
    ImageRenderer,
    InteractiveRenderer,
    ListRenderer,
    TextRenderer,
    WorkflowRenderer,
)

# Initialize logger for this module
logger = LoggerManager.get_logger(__name__)


class RendererManager:
    """
    Менеджер для координации всех рендереров контента.
    Автоматически выбирает подходящий рендерер для каждого типа контента.
    """

    def __init__(self, theme_manager=None):
        """
        Инициализация менеджера рендеринга.

        Args:
            theme_manager: Менеджер тем для стилизации
        """
        logger.info("Initializing RendererManager")
        self.theme_manager = theme_manager
        self.renderers: List[BaseRenderer] = []
        self.renderer_map: Dict[str, BaseRenderer] = {}  # Initialize state logger for comprehensive tracking
        self.state_logger = StateLogger("RendererManager")
        self.state_logger.log_operation_start("initialization")

        try:
            self._initialize_renderers()
            self._build_renderer_map()
            logger.debug(f"RendererManager initialized with {len(self.renderers)} renderers")
        except Exception as e:
            logger.error(f"Failed to initialize RendererManager: {e}")
            raise

    def _initialize_renderers(self) -> None:
        """Инициализирует все доступные рендереры."""
        self.state_logger.log_operation_start("renderer_initialization")

        self.renderers = [
            TextRenderer(self.theme_manager),
            ImageRenderer(self.theme_manager),
            CodeRenderer(self.theme_manager),
            ListRenderer(self.theme_manager),
            InteractiveRenderer(self.theme_manager),
            WorkflowRenderer(self.theme_manager),
        ]

        self.state_logger.log_operation_end("renderer_initialization", success=True, count=len(self.renderers))

    def _build_renderer_map(self) -> None:
        """Строит карту соответствия типов контента и рендереров."""
        self.state_logger.log_operation_start("building_renderer_map")
        self.renderer_map = {}

        for renderer in self.renderers:
            supported_types = renderer.get_supported_types()
            for content_type in supported_types:
                self.renderer_map[content_type] = renderer

        self.state_logger.log_operation_end("building_renderer_map", success=True, map_size=len(self.renderer_map))

    def render_block(self, content: Dict[str, Any]) -> Optional[QWidget]:
        """
        Рендерит блок контента, выбрав подходящий рендерер.

        Args:
            content: Словарь с данными контента

        Returns:
            QWidget: Созданный виджет или None если рендерер не найден
        """
        if not content or not isinstance(content, dict):
            logger.warning("Invalid content format provided to render_block")
            return self._create_error_widget("Invalid content format")

        content_type = content.get("type", "")
        if not content_type:
            logger.warning("Content type not specified in render_block")
            return self._create_error_widget("Content type not specified")

        logger.debug(f"Rendering content block of type: {content_type}")

        # Ищем подходящий рендерер
        renderer = self.renderer_map.get(content_type)
        if not renderer:
            logger.error(f"No renderer found for content type: {content_type}")
            return self._create_error_widget(f"No renderer found for type: {content_type}")

        try:
            # Рендерим контент
            widget = renderer.render(content)
            if widget:
                logger.debug(f"Successfully rendered content block of type: {content_type}")
                return widget
            else:
                logger.error(f"Renderer failed to create widget for type: {content_type}")
                return self._create_error_widget(f"Renderer failed to create widget for: {content_type}")

        except Exception as e:
            logger.error(f"Error rendering {content_type}: {e}")
            error_message = f"Error rendering {content_type}: {str(e)}"
            return self._create_error_widget(error_message)

    def render_content_list(self, content_list: List[Dict[str, Any]]) -> List[QWidget]:
        """
        Рендерит список блоков контента.

        Args:
            content_list: Список блоков контента

        Returns:
            List[QWidget]: Список созданных виджетов
        """
        logger.debug(f"Rendering content list with {len(content_list)} blocks")
        widgets = []

        for content_block in content_list:
            widget = self.render_block(content_block)
            if widget:
                widgets.append(widget)

        logger.debug(f"Successfully rendered {len(widgets)} widgets from content list")
        return widgets

    def get_supported_types(self) -> List[str]:
        """
        Возвращает список всех поддерживаемых типов контента.

        Returns:
            List[str]: Список типов контента
        """
        supported_types = set()
        for renderer in self.renderers:
            supported_types.update(renderer.get_supported_types())
        return sorted(supported_types)

    def add_renderer(self, renderer: BaseRenderer) -> None:
        """
        Добавляет новый рендерер в систему.

        Args:
            renderer: Экземпляр рендерера
        """
        if not isinstance(renderer, BaseRenderer):
            raise ValueError("Renderer must inherit from BaseRenderer")

        logger.info(f"Adding renderer: {renderer.__class__.__name__}")
        self.renderers.append(renderer)

        # Обновляем карту рендереров
        supported_types = renderer.get_supported_types()
        for content_type in supported_types:
            self.renderer_map[content_type] = renderer

    def remove_renderer(self, renderer_class: type) -> bool:
        """
        Удаляет рендерер указанного класса.

        Args:
            renderer_class: Класс рендерера для удаления

        Returns:
            bool: True если рендерер был удален
        """
        removed = False
        renderers_to_remove = []

        for renderer in self.renderers:
            if isinstance(renderer, renderer_class):
                renderers_to_remove.append(renderer)
                removed = True

        # Удаляем найденные рендереры
        for renderer in renderers_to_remove:
            logger.info(f"Removing renderer: {renderer.__class__.__name__}")
            self.renderers.remove(renderer)

        # Пересобираем карту
        if removed:
            self._build_renderer_map()

        return removed

    def get_renderer_for_type(self, content_type: str) -> Optional[BaseRenderer]:
        """
        Получает рендерер для указанного типа контента.

        Args:
            content_type: Тип контента

        Returns:
            BaseRenderer: Рендерер или None если не найден
        """
        return self.renderer_map.get(content_type)

    def update_theme_manager(self, theme_manager) -> None:
        """
        Обновляет менеджер тем для всех рендереров.

        Args:
            theme_manager: Новый менеджер тем
        """
        logger.info("Updating theme manager for all renderers")
        self.theme_manager = theme_manager

        for renderer in self.renderers:
            renderer.theme_manager = theme_manager

    def _create_error_widget(self, message: str) -> QWidget:
        """
        Создает виджет для отображения ошибки рендеринга.

        Args:
            message: Сообщение об ошибке

        Returns:
            QWidget: Виджет с сообщением об ошибке
        """
        error_label = QLabel(f"❌ Render Error: {message}")
        error_label.setWordWrap(True)

        # Базовая стилизация ошибки
        error_style = """
            QLabel {
                color: #d32f2f;
                background-color: #ffebee;
                border: 1px solid #f8bbd9;
                border-radius: 4px;
                padding: 8px;
                margin: 4px 0px;
            }
        """

        # Применяем стиль из темы если доступен
        if self.theme_manager:
            error_color = self.theme_manager.get_color("error")
            surface_color = self.theme_manager.get_color("surface")
            if error_color and surface_color:
                error_style = f"""
                    QLabel {{
                        color: {error_color.name()};
                        background-color: {surface_color.name()};
                        border: 1px solid {error_color.name()};
                        border-radius: 4px;
                        padding: 8px;
                        margin: 4px 0px;
                    }}
                """

        error_label.setStyleSheet(error_style)
        return error_label

    def get_renderer_info(self) -> Dict[str, Any]:
        """
        Получает информацию о зарегистрированных рендерерах.

        Returns:
            Dict: Информация о рендерерах
        """
        info = {"total_renderers": len(self.renderers), "supported_types": self.get_supported_types(), "renderers": []}

        for renderer in self.renderers:
            renderer_info = {
                "class": renderer.__class__.__name__,
                "supported_types": renderer.get_supported_types(),
                "has_theme_manager": renderer.theme_manager is not None,
            }
            info["renderers"].append(renderer_info)

        return info
