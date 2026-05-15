"""
seed_data.py — static product catalog for the synthetic generator.

Keeping the catalog fixed means every generated sale references a real
product_id and category. Silver/Gold models can join on these without
ever hitting nulls from a missing product.
"""

PRODUCTS: list[dict] = [
    {"product_id": f"SKU-{i:03d}", "name": name, "category": category, "unit_price_brl": price}
    for i, (name, category, price) in enumerate(
        [
            ("Notebook Lenovo IdeaPad", "electronics", 2899.90),
            ("Notebook Dell Inspiron", "electronics", 3299.90),
            ("Smartphone Samsung Galaxy A54", "electronics", 1599.90),
            ("Smartphone Motorola Edge 40", "electronics", 1299.90),
            ("Smart TV LG 50\"", "electronics", 2199.90),
            ("Fone Bluetooth JBL", "electronics", 299.90),
            ("Teclado Mecânico Redragon", "electronics", 349.90),
            ("Mouse Gamer Logitech", "electronics", 199.90),
            ("Monitor Dell 24\"", "electronics", 1099.90),
            ("SSD Kingston 480GB", "electronics", 229.90),
            ("Tênis Nike Air Max", "apparel", 599.90),
            ("Tênis Adidas Ultraboost", "apparel", 699.90),
            ("Camiseta Polo Ralph Lauren", "apparel", 349.90),
            ("Calça Jeans Levi's 501", "apparel", 299.90),
            ("Jaqueta Columbia", "apparel", 499.90),
            ("Mochila Samsonite", "apparel", 399.90),
            ("Óculos Ray-Ban Wayfarer", "apparel", 649.90),
            ("Relógio Casio G-Shock", "apparel", 799.90),
            ("Tênis Vans Old Skool", "apparel", 399.90),
            ("Boné New Era", "apparel", 149.90),
            ("Frigideira Tramontina 26cm", "home", 89.90),
            ("Panela de Pressão Rochedo 4.5L", "home", 129.90),
            ("Liquidificador Oster 1200W", "home", 199.90),
            ("Cafeteira Nespresso Essenza", "home", 499.90),
            ("Aspirador Robô iRobot", "home", 1499.90),
            ("Ventilador Arno Silence Force", "home", 249.90),
            ("Jogo de Cama Queen Buddemeyer", "home", 299.90),
            ("Travesseiro Fibrasca", "home", 79.90),
            ("Escova Oral-B IO Series", "home", 349.90),
            ("Air Fryer Philips Walita", "home", 599.90),
            ("Proteína Whey Gold Standard 900g", "health", 199.90),
            ("Creatina Monohidratada 300g", "health", 79.90),
            ("Vitamina C 1000mg 60 caps", "health", 49.90),
            ("Ômega 3 1000mg 120 caps", "health", 59.90),
            ("BCAA 2400 120 caps", "health", 69.90),
            ("Multivitamínico Centrum", "health", 89.90),
            ("Proteína Vegana Vegan Protein", "health", 149.90),
            ("Colágeno Hidrolisado 300g", "health", 69.90),
            ("Spirulina 500mg 120 caps", "health", 79.90),
            ("Pré-Treino C4 Original", "health", 129.90),
            ("O Senhor dos Anéis", "books", 89.90),
            ("Sapiens - Uma Breve História", "books", 59.90),
            ("Pai Rico, Pai Pobre", "books", 49.90),
            ("Hábitos Atômicos", "books", 54.90),
            ("O Poder do Hábito", "books", 49.90),
            ("Clean Code", "books", 109.90),
            ("Design de Sistemas", "books", 129.90),
            ("Python Fluente", "books", 119.90),
            ("A Startup Enxuta", "books", 54.90),
            ("Mindset - A Nova Psicologia", "books", 49.90),
        ],
        start=1,
    )
]

CATEGORIES: list[str] = ["electronics", "apparel", "home", "health", "books"]
