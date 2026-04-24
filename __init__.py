# routes/__init__.py
# This file makes 'routes' a Python package
# so Flask can import from it

from .products  import products_bp
from .customers import customers_bp
from .orders    import orders_bp
from .analytics import analytics_bp