# AgroVista Backend API Endpoints

## Root Endpoint
- **GET** `/` - Welcome message with API info

## Terrains (`/terrains`)
- **GET** `/terrains/` - Get all terrains
- **GET** `/terrains/{terrain_id}` - Get terrain by ID  
- **POST** `/terrains/` - Create new terrain
- **GET** `/terrains/listar` - Legacy: Get all terrains (Spanish)
- **GET** `/terrains/obtener/{terreno_id}` - Legacy: Get terrain by ID (Spanish)
- **POST** `/terrains/crear` - Legacy: Create terrain (Spanish)

## Parcels (`/parcels`)  
- **GET** `/parcels/` - Get all parcels
- **GET** `/parcels/by-terrain/{terrain_id}` - Get parcels by terrain ID
- **GET** `/parcels/{parcel_id}` - Get parcel by ID
- **POST** `/parcels/` - Create new parcel
- **GET** `/parcels/listar` - Legacy: Get all parcels (Spanish)
- **GET** `/parcels/listar-por-terreno/{terreno_id}` - Legacy: Get parcels by terrain (Spanish)
- **GET** `/parcels/obtener/{parcela_id}` - Legacy: Get parcel by ID (Spanish)
- **POST** `/parcels/crear` - Legacy: Create parcel (Spanish)

## Activities (`/activities`)
- **GET** `/activities/` - Get all activities
- **POST** `/activities/` - Register new activity
- **GET** `/activities/{activity_id}` - Get activity by ID
- **PUT** `/activities/{activity_id}` - Update existing activity
- **DELETE** `/activities/{activity_id}` - Delete activity
- **GET** `/activities/by-parcel/{parcel_id}` - Get activities for parcel
- **POST** `/activities/bulk/` - Register multiple activities
- **POST** `/activities/details/` - Register multiple activity details
- **POST** `/activities/registrar/` - Legacy: Register activity (Spanish)
- **GET** `/activities/por-parcela/{parcela_id}` - Legacy: Get activities by parcel (Spanish)
- **POST** `/activities/masivo/` - Legacy: Register bulk activities (Spanish)
- **POST** `/activities/detalles-masivo/` - Legacy: Register bulk activity details (Spanish)

## Economy (`/economy`)
### Transactions
- **POST** `/economy/transaction/` - Create financial transaction
- **GET** `/economy/transaction/{id}` - Get transaction by ID
- **GET** `/economy/transactions/` - List all transactions

### Budgets  
- **POST** `/economy/budget/` - Create new budget
- **GET** `/economy/budget/{id}` - Get budget by ID
- **GET** `/economy/budgets/` - List all budgets

### Analysis
- **GET** `/economy/comparison/` - Compare budgeted vs actual expenses
- **GET** `/economy/global-summary/` - Get global economic summary
- **GET** `/economy/monthly-comparison/` - Get monthly expense comparison

### Legacy Economy (Spanish)
- **POST** `/economy/transaccion/` - Legacy: Create transaction
- **GET** `/economy/transaccion/{id}` - Legacy: Get transaction
- **GET** `/economy/transacciones/` - Legacy: List transactions
- **POST** `/economy/presupuesto/` - Legacy: Create budget
- **GET** `/economy/presupuesto/{id}` - Legacy: Get budget
- **GET** `/economy/presupuestos/` - Legacy: List budgets
- **GET** `/economy/comparativo/` - Legacy: Budget vs actual comparison
- **GET** `/economy/resumen-global/` - Legacy: Global economic summary
- **GET** `/economy/comparativo-mensual/` - Legacy: Monthly comparison

## Inventory (`/inventory`)
### Inventory Items
- **POST** `/inventory/` - Create inventory item
- **GET** `/inventory/{id}` - Get inventory item by ID
- **GET** `/inventory/` - List all inventory items

### Inventory Events
- **POST** `/inventory/event/` - Create inventory movement event
- **GET** `/inventory/event/{id}` - Get inventory event by ID
- **GET** `/inventory/events/` - List all inventory events

### Legacy Inventory (Spanish)
- **POST** `/inventory/inventario/` - Legacy: Create inventory
- **GET** `/inventory/inventario/{id}` - Legacy: Get inventory
- **GET** `/inventory/inventarios/` - Legacy: List inventories
- **POST** `/inventory/evento/` - Legacy: Create inventory event
- **GET** `/inventory/evento/{id}` - Legacy: Get inventory event
- **GET** `/inventory/eventos/` - Legacy: List inventory events

## Chat (`/chat`) 
- **POST** `/chat` - AI assistant chat interactions

## Locations (`/locations`)
- **POST** `/locations/` - Create new location
- **GET** `/locations/{location_id}` - Get location by ID
- **POST** `/locations/crear` - Legacy: Create location (Spanish)
- **GET** `/locations/obtener/{ubicacion_id}` - Legacy: Get location (Spanish)

## Control & KPIs (`/control`)
### Change History
- **POST** `/control/change/` - Register new change
- **GET** `/control/change/{id}` - Get change record by ID
- **GET** `/control/changes/` - List all change records

### Indicators
- **POST** `/control/indicator/` - Create KPI indicator
- **GET** `/control/indicator/{id}` - Get indicator by ID
- **GET** `/control/indicators/` - List all KPI indicators

### Legacy Control (Spanish)
- **POST** `/control/cambio/` - Legacy: Register change
- **GET** `/control/cambio/{id}` - Legacy: Get change
- **GET** `/control/cambios/` - Legacy: List changes
- **POST** `/control/indicador/` - Legacy: Create indicator
- **GET** `/control/indicador/{id}` - Legacy: Get indicator
- **GET** `/control/indicadores/` - Legacy: List indicators

## Simulation (`/simulation`)
### Simulations
- **POST** `/simulation/` - Create new simulation
- **GET** `/simulation/{id}` - Get simulation by ID
- **GET** `/simulation/` - List all simulations
- **POST** `/simulation/simulate` - Run projection simulation

### Biological Parameters
- **POST** `/simulation/parameter/` - Create biological parameter
- **GET** `/simulation/parameter/{id}` - Get biological parameter by ID
- **GET** `/simulation/parameters/` - List all biological parameters

### Legacy Simulation (Spanish)
- **POST** `/simulation/simulacion/` - Legacy: Create simulation
- **GET** `/simulation/simulacion/{id}` - Legacy: Get simulation
- **GET** `/simulation/simulaciones/` - Legacy: List simulations
- **POST** `/simulation/parametro/` - Legacy: Create biological parameter
- **GET** `/simulation/parametro/{id}` - Legacy: Get biological parameter
- **GET** `/simulation/parametros/` - Legacy: List biological parameters
- **POST** `/simulation/simular` - Legacy: Run simulation projection

---

**Total Endpoints:** 85+ endpoints across 9 main modules, including both English and Spanish legacy versions for backward compatibility. All endpoints support full CRUD operations where applicable and include comprehensive agricultural management functionality covering terrains, parcels, activities, economics, inventory, chat AI, locations, control/KPIs, and biological simulations.