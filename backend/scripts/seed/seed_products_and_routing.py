#!/usr/bin/env python3
"""
Seed master data: Products, Routings, Routing Operations, Resource Requirements.

This script creates manufacturing master data that forms the foundation for
production orders and work orders.

Usage:
  cd backend
    .venv\\Scripts\\python scripts/seed/seed_products_and_routing.py

Database: localhost:5432/mes (Docker postgres_data volume)
"""

import uuid
from sqlalchemy import select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.routing import Routing, RoutingOperation
from app.models.resource_requirement import ResourceRequirement


TENANT_ID = "default"


def _gen_id() -> str:
    """Generate a UUID for database IDs."""
    return str(uuid.uuid4())


def seed_products():
    """Create test products (FINISHED_GOOD, SEMI_FINISHED, COMPONENT)."""
    db = SessionLocal()
    try:
        print("\n=== PRODUCTS ===")

        products_config = [
            {
                "product_code": "WIDGET-A",
                "product_name": "Widget A - Standard",
                "product_type": "FINISHED_GOOD",
                "description": "Standard widget assembly (red variant)",
            },
            {
                "product_code": "WIDGET-B",
                "product_name": "Widget B - Premium",
                "product_type": "FINISHED_GOOD",
                "description": "Premium widget assembly (blue variant)",
            },
            {
                "product_code": "FRAME-001",
                "product_name": "Frame Assembly",
                "product_type": "SEMI_FINISHED",
                "description": "Intermediate component - frame for widgets",
            },
            {
                "product_code": "MOTOR-STD",
                "product_name": "Standard Motor",
                "product_type": "COMPONENT",
                "description": "Standard 24V DC motor",
            },
            {
                "product_code": "BEARING-001",
                "product_name": "Precision Bearing",
                "product_type": "COMPONENT",
                "description": "High-precision ball bearing, imported",
            },
            {
                "product_code": "CONNECTOR-A",
                "product_name": "Connector Type A",
                "product_type": "COMPONENT",
                "description": "3-pin connector for assembly",
            },
        ]

        products = {}
        for config in products_config:
            existing = db.scalar(
                select(Product).where(
                    Product.product_code == config["product_code"],
                    Product.tenant_id == TENANT_ID,
                )
            )
            if existing:
                products[config["product_code"]] = existing
                print(f"  ✓ {config['product_code']} (existing)")
                continue

            product = Product(
                product_id=_gen_id(),
                tenant_id=TENANT_ID,
                product_code=config["product_code"],
                product_name=config["product_name"],
                product_type=config["product_type"],
                lifecycle_status="DRAFT",
                description=config["description"],
            )
            db.add(product)
            db.flush()
            products[config["product_code"]] = product
            print(f"  ✓ {config['product_code']}: {config['product_name']}")

        db.commit()
        return products

    finally:
        db.close()


def seed_routings_and_operations(products):
    """
    Create routings (manufacturing sequences) for products.

    Structure:
    - WIDGET-A → R-WIDGET-A (3 operations)
    - WIDGET-B → R-WIDGET-B (4 operations)
    - FRAME-001 → R-FRAME (2 operations)
    """
    db = SessionLocal()
    try:
        print("\n=== ROUTINGS & ROUTING OPERATIONS ===")

        # Routing 1: WIDGET-A (3 operations)
        routing_widget_a = _create_or_get_routing(
            db,
            product_id=products["WIDGET-A"].product_id,
            routing_code="R-WIDGET-A",
            routing_name="Standard Widget A Routing",
        )
        _add_routing_operations(
            db,
            routing_id=routing_widget_a.routing_id,
            operations=[
                {
                    "operation_code": "OP-10",
                    "operation_name": "Assembly Frame",
                    "sequence_no": 10,
                    "standard_cycle_time": 15.0,
                    "required_resource_type": "ASSEMBLY_STATION",
                },
                {
                    "operation_code": "OP-20",
                    "operation_name": "Install Motor",
                    "sequence_no": 20,
                    "standard_cycle_time": 8.0,
                    "required_resource_type": "ASSEMBLY_STATION",
                },
                {
                    "operation_code": "OP-30",
                    "operation_name": "Test & QC",
                    "sequence_no": 30,
                    "standard_cycle_time": 5.0,
                    "required_resource_type": "QC_STATION",
                },
            ],
        )

        # Routing 2: WIDGET-B (4 operations)
        routing_widget_b = _create_or_get_routing(
            db,
            product_id=products["WIDGET-B"].product_id,
            routing_code="R-WIDGET-B",
            routing_name="Premium Widget B Routing",
        )
        _add_routing_operations(
            db,
            routing_id=routing_widget_b.routing_id,
            operations=[
                {
                    "operation_code": "OP-10",
                    "operation_name": "Assembly Frame",
                    "sequence_no": 10,
                    "standard_cycle_time": 18.0,
                    "required_resource_type": "ASSEMBLY_STATION",
                },
                {
                    "operation_code": "OP-20",
                    "operation_name": "Install Premium Motor",
                    "sequence_no": 20,
                    "standard_cycle_time": 10.0,
                    "required_resource_type": "ASSEMBLY_STATION",
                },
                {
                    "operation_code": "OP-25",
                    "operation_name": "Install Bearing Pack",
                    "sequence_no": 25,
                    "standard_cycle_time": 6.0,
                    "required_resource_type": "ASSEMBLY_STATION",
                },
                {
                    "operation_code": "OP-30",
                    "operation_name": "Extended Test & QC",
                    "sequence_no": 30,
                    "standard_cycle_time": 8.0,
                    "required_resource_type": "QC_STATION",
                },
            ],
        )

        # Routing 3: FRAME-001 (2 operations)
        routing_frame = _create_or_get_routing(
            db,
            product_id=products["FRAME-001"].product_id,
            routing_code="R-FRAME",
            routing_name="Frame Assembly Routing",
        )
        _add_routing_operations(
            db,
            routing_id=routing_frame.routing_id,
            operations=[
                {
                    "operation_code": "OP-10",
                    "operation_name": "Cut & Prepare",
                    "sequence_no": 10,
                    "standard_cycle_time": 12.0,
                    "required_resource_type": "CUTTING_STATION",
                },
                {
                    "operation_code": "OP-20",
                    "operation_name": "Weld Assembly",
                    "sequence_no": 20,
                    "standard_cycle_time": 20.0,
                    "required_resource_type": "WELDING_STATION",
                },
            ],
        )

        db.commit()

    finally:
        db.close()


def seed_resource_requirements():
    """
    Create resource requirements linking routing operations to capabilities.

    Examples:
    - OP-10 (Assembly Frame) requires 2x ASSEMBLY_WORKER
    - OP-30 (Test & QC) requires 1x QC_INSPECTOR
    - OP-20 (Install Motor) requires 1x ASSEMBLY_WORKER + 1x MOTOR_SPECIALIST
    """
    db = SessionLocal()
    try:
        print("\n=== RESOURCE REQUIREMENTS ===")

        # Get routings
        routing_a = db.scalar(
            select(Routing).where(Routing.routing_code == "R-WIDGET-A")
        )
        routing_b = db.scalar(
            select(Routing).where(Routing.routing_code == "R-WIDGET-B")
        )
        routing_frame = db.scalar(
            select(Routing).where(Routing.routing_code == "R-FRAME")
        )

        if not all([routing_a, routing_b, routing_frame]):
            print("  ⚠ Routings not found, skipping resource requirements")
            return

        requirements_config = []

        # WIDGET-A requirements
        if routing_a:
            op_10 = db.scalar(
                select(RoutingOperation).where(
                    RoutingOperation.routing_id == routing_a.routing_id,
                    RoutingOperation.sequence_no == 10,
                )
            )
            op_20 = db.scalar(
                select(RoutingOperation).where(
                    RoutingOperation.routing_id == routing_a.routing_id,
                    RoutingOperation.sequence_no == 20,
                )
            )
            op_30 = db.scalar(
                select(RoutingOperation).where(
                    RoutingOperation.routing_id == routing_a.routing_id,
                    RoutingOperation.sequence_no == 30,
                )
            )

            if op_10:
                requirements_config.append(
                    {
                        "routing_id": routing_a.routing_id,
                        "operation_id": op_10.operation_id,
                        "required_resource_type": "ASSEMBLY_STATION",
                        "required_capability_code": "ASSEMBLY_WORKER",
                        "quantity_required": 2,
                        "notes": "2 assembly workers for frame assembly",
                    }
                )
            if op_20:
                requirements_config.extend(
                    [
                        {
                            "routing_id": routing_a.routing_id,
                            "operation_id": op_20.operation_id,
                            "required_resource_type": "ASSEMBLY_STATION",
                            "required_capability_code": "ASSEMBLY_WORKER",
                            "quantity_required": 1,
                            "notes": "General assembly worker for motor installation",
                        },
                        {
                            "routing_id": routing_a.routing_id,
                            "operation_id": op_20.operation_id,
                            "required_resource_type": "ASSEMBLY_STATION",
                            "required_capability_code": "MOTOR_SPECIALIST",
                            "quantity_required": 1,
                            "notes": "Specialist for motor quality check",
                        },
                    ]
                )
            if op_30:
                requirements_config.append(
                    {
                        "routing_id": routing_a.routing_id,
                        "operation_id": op_30.operation_id,
                        "required_resource_type": "QC_STATION",
                        "required_capability_code": "QC_INSPECTOR",
                        "quantity_required": 1,
                        "notes": "QC inspector for final test",
                    }
                )

        # WIDGET-B requirements (similar with premium specs)
        if routing_b:
            op_10 = db.scalar(
                select(RoutingOperation).where(
                    RoutingOperation.routing_id == routing_b.routing_id,
                    RoutingOperation.sequence_no == 10,
                )
            )
            op_30 = db.scalar(
                select(RoutingOperation).where(
                    RoutingOperation.routing_id == routing_b.routing_id,
                    RoutingOperation.sequence_no == 30,
                )
            )

            if op_10:
                requirements_config.append(
                    {
                        "routing_id": routing_b.routing_id,
                        "operation_id": op_10.operation_id,
                        "required_resource_type": "ASSEMBLY_STATION",
                        "required_capability_code": "ASSEMBLY_WORKER",
                        "quantity_required": 2,
                        "notes": "Premium assembly requires 2 workers",
                    }
                )
            if op_30:
                requirements_config.append(
                    {
                        "routing_id": routing_b.routing_id,
                        "operation_id": op_30.operation_id,
                        "required_resource_type": "QC_STATION",
                        "required_capability_code": "QC_INSPECTOR_SENIOR",
                        "quantity_required": 1,
                        "notes": "Senior QC for premium product",
                    }
                )

        # FRAME requirements
        if routing_frame:
            op_20 = db.scalar(
                select(RoutingOperation).where(
                    RoutingOperation.routing_id == routing_frame.routing_id,
                    RoutingOperation.sequence_no == 20,
                )
            )

            if op_20:
                requirements_config.append(
                    {
                        "routing_id": routing_frame.routing_id,
                        "operation_id": op_20.operation_id,
                        "required_resource_type": "WELDING_STATION",
                        "required_capability_code": "WELDER",
                        "quantity_required": 1,
                        "notes": "Certified welder for frame assembly",
                    }
                )

        # Create requirements
        for config in requirements_config:
            existing = db.scalar(
                select(ResourceRequirement).where(
                    ResourceRequirement.operation_id == config["operation_id"],
                    ResourceRequirement.required_capability_code
                    == config["required_capability_code"],
                )
            )
            if existing:
                print(
                    f"  ✓ {config['required_capability_code']} for OP {config['operation_id'][:8]} (existing)"
                )
                continue

            rr = ResourceRequirement(
                requirement_id=_gen_id(),
                tenant_id=TENANT_ID,
                routing_id=config["routing_id"],
                operation_id=config["operation_id"],
                required_resource_type=config["required_resource_type"],
                required_capability_code=config["required_capability_code"],
                quantity_required=config["quantity_required"],
                notes=config.get("notes"),
            )
            db.add(rr)
            db.flush()
            print(
                f"  ✓ {config['required_capability_code']} (qty: {config['quantity_required']})"
            )

        db.commit()

    finally:
        db.close()


def _create_or_get_routing(db, product_id: str, routing_code: str, routing_name: str) -> Routing:
    """Create or get a routing by code."""
    existing = db.scalar(
        select(Routing).where(
            Routing.routing_code == routing_code,
            Routing.tenant_id == TENANT_ID,
        )
    )
    if existing:
        print(f"  ✓ {routing_code}: {routing_name} (existing)")
        return existing

    routing = Routing(
        routing_id=_gen_id(),
        tenant_id=TENANT_ID,
        product_id=product_id,
        routing_code=routing_code,
        routing_name=routing_name,
        lifecycle_status="DRAFT",
    )
    db.add(routing)
    db.flush()
    print(f"  ✓ {routing_code}: {routing_name}")
    return routing


def _add_routing_operations(db, routing_id: str, operations: list) -> None:
    """Add operations to a routing if they don't exist."""
    for op_config in operations:
        existing = db.scalar(
            select(RoutingOperation).where(
                RoutingOperation.routing_id == routing_id,
                RoutingOperation.sequence_no == op_config["sequence_no"],
            )
        )
        if existing:
            continue

        op = RoutingOperation(
            operation_id=_gen_id(),
            tenant_id=TENANT_ID,
            routing_id=routing_id,
            operation_code=op_config["operation_code"],
            operation_name=op_config["operation_name"],
            sequence_no=op_config["sequence_no"],
            standard_cycle_time=op_config.get("standard_cycle_time"),
            required_resource_type=op_config.get("required_resource_type"),
        )
        db.add(op)
        db.flush()


def main():
    """Run all seed operations."""
    print("\n" + "=" * 60)
    print("SEED MASTER DATA: PRODUCTS & ROUTINGS")
    print("=" * 60)

    init_db = None
    try:
        from app.db.init_db import init_db as init_db_func
        init_db = init_db_func
    except ImportError:
        pass

    products = seed_products()
    seed_routings_and_operations(products)
    seed_resource_requirements()

    print("\n" + "=" * 60)
    print("✓ ALL MASTER DATA SEEDED SUCCESSFULLY")
    print("=" * 60)
    print("\nData Summary:")
    print("- Products: 6 total")
    print("  - Finished Goods: WIDGET-A, WIDGET-B")
    print("  - Semi-Finished: FRAME-001")
    print("  - Components: MOTOR-STD, BEARING-001, CONNECTOR-A")
    print("\n- Routings: 3 total")
    print("  - R-WIDGET-A: 3 operations")
    print("  - R-WIDGET-B: 4 operations")
    print("  - R-FRAME: 2 operations")
    print("\n- Resource Requirements: Multi-skill assignments")
    print("  - Assembly workers, QC inspectors, Welders, Specialists")
    print()


if __name__ == "__main__":
    main()
