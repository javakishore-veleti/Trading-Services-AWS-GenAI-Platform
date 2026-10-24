from common.dtos.req_resp_dtos import GetProductRequest, ListProductsRequest, ProductDto, ProductRowDto, ProductRowsDto
from dao.interfaces import CatalogDao


class CatalogDaoImpl(CatalogDao):
    _products: list[ProductDto] = [
        ProductDto(product_id="SPOT-EURUSD", name="EUR/USD Spot", product_type="spot", pair="EUR/USD", base="EUR", quote="USD", tenor="spot", settlement="T+2", min_notional_usd=10000, max_notional_usd=50000000, customer_segments=["corporate", "institutional", "private"]),
        ProductDto(product_id="SPOT-GBPUSD", name="GBP/USD Spot", product_type="spot", pair="GBP/USD", base="GBP", quote="USD", tenor="spot", settlement="T+2", min_notional_usd=10000, max_notional_usd=40000000, customer_segments=["corporate", "institutional", "private"]),
        ProductDto(product_id="SPOT-USDJPY", name="USD/JPY Spot", product_type="spot", pair="USD/JPY", base="USD", quote="JPY", tenor="spot", settlement="T+2", min_notional_usd=10000, max_notional_usd=50000000, customer_segments=["corporate", "institutional", "private"]),
        ProductDto(product_id="SPOT-USDCHF", name="USD/CHF Spot", product_type="spot", pair="USD/CHF", base="USD", quote="CHF", tenor="spot", settlement="T+2", min_notional_usd=10000, max_notional_usd=25000000, customer_segments=["corporate", "institutional"]),
        ProductDto(product_id="SPOT-AUDUSD", name="AUD/USD Spot", product_type="spot", pair="AUD/USD", base="AUD", quote="USD", tenor="spot", settlement="T+2", min_notional_usd=10000, max_notional_usd=25000000, customer_segments=["corporate", "institutional"]),
        ProductDto(product_id="FWD-EURUSD-1M", name="EUR/USD 1M Forward", product_type="forward", pair="EUR/USD", base="EUR", quote="USD", tenor="1M", settlement="1M", min_notional_usd=25000, max_notional_usd=40000000, customer_segments=["corporate", "institutional"]),
        ProductDto(product_id="FWD-USDJPY-3M", name="USD/JPY 3M Forward", product_type="forward", pair="USD/JPY", base="USD", quote="JPY", tenor="3M", settlement="3M", min_notional_usd=25000, max_notional_usd=40000000, customer_segments=["corporate", "institutional"]),
        ProductDto(product_id="SWAP-EURUSD", name="EUR/USD FX Swap", product_type="swap", pair="EUR/USD", base="EUR", quote="USD", tenor="spot-1M", settlement="split", min_notional_usd=50000, max_notional_usd=75000000, customer_segments=["institutional"]),
        ProductDto(product_id="NDF-USDINR", name="USD/INR NDF", product_type="ndf", pair="USD/INR", base="USD", quote="INR", tenor="1M", settlement="cash", min_notional_usd=50000, max_notional_usd=20000000, customer_segments=["corporate", "institutional"]),
        ProductDto(product_id="NDF-USDKRW", name="USD/KRW NDF", product_type="ndf", pair="USD/KRW", base="USD", quote="KRW", tenor="1M", settlement="cash", min_notional_usd=50000, max_notional_usd=20000000, customer_segments=["corporate", "institutional"]),
        ProductDto(product_id="OPT-EURUSD-VAN", name="EUR/USD Vanilla Option", product_type="vanilla-option", pair="EUR/USD", base="EUR", quote="USD", tenor="3M", settlement="delivery", min_notional_usd=100000, max_notional_usd=25000000, customer_segments=["institutional", "private"]),
        ProductDto(product_id="OPT-GBPUSD-BAR", name="GBP/USD Barrier Option", product_type="barrier-option", pair="GBP/USD", base="GBP", quote="USD", tenor="3M", settlement="delivery", min_notional_usd=250000, max_notional_usd=15000000, customer_segments=["institutional"]),
    ]

    def find_products(self, request: ListProductsRequest) -> ProductRowsDto:
        rows = CatalogDaoImpl._products
        if request.product_type:
            rows = [row for row in rows if row.product_type == request.product_type]
        if request.segment:
            rows = [row for row in rows if request.segment in row.customer_segments]
        return ProductRowsDto(products=rows)

    def find_product(self, request: GetProductRequest) -> ProductRowDto:
        found = next((row for row in CatalogDaoImpl._products if row.product_id == request.product_id), None)
        return ProductRowDto(product=found)
