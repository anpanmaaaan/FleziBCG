// Mock data for MOM system

export interface ProductionOrder {
  id: string;
  serialNumber: string;
  lotId?: string;
  routeId: string;
  machineNumber?: string;
  quantity: number;
  plannedCompletionDate: string;
  releasedDate: string;
  releaseDate: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'PENDING' | 'LATE';
  progress: number;
  line?: string;
  // New fields
  customer?: string;
  priority?: 'High' | 'Medium' | 'Low';
  plannedStartDate?: string;
  actualStartDate?: string;
  actualCompletionDate?: string;
  assignee?: string;
  department?: string;
  productName?: string;
  materialCode?: string;
}

export interface Operation {
  id: string;
  productionOrderId: string;
  productionLine: string;
  workstation: string;
  remainingTime: string;
  progress: number;
  status: 'Ready' | 'In Progress' | 'Completed';
  timing: 'On time' | 'Late' | 'Early';
}

export interface Route {
  id: string;
  name: string;
  lastUpdated: string;
  status: 'Active' | 'Inactive';
}

export interface OrderCard {
  id: string;
  orderId: string;
  quantity: number;
  progress: number;
  status: 'Late' | 'On Time' | 'Completed';
  workersCount: number;
}

export interface ProductionLine {
  id: string;
  name: string;
  shift: string;
  lateStatus?: 'Late';
  orders: OrderCard[];
}

// Mock Production Orders
export const productionOrders: ProductionOrder[] = [
  {
    id: '1',
    serialNumber: '01082024',
    routeId: 'DMES-R11',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: '2',
    serialNumber: '01_16102024_BLK2',
    routeId: 'DMES-R11',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: '3',
    serialNumber: '01_16P0989_DL3',
    routeId: 'DMES-R11',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: '4',
    serialNumber: '01_PO32174049_DL1',
    routeId: 'DMES-R1',
    machineNumber: 'PO32174049_DL1',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: '5',
    serialNumber: '02082024',
    routeId: 'DMES-R11',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: '6',
    serialNumber: '02_16102024_BLK2',
    routeId: 'DMES-R11',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: 'P02-BLK1',
    serialNumber: 'P02-BLK1',
    routeId: 'DMES-R8',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: 'PO03-BLK2',
    serialNumber: 'PO03-BLK2',
    routeId: 'DMES-R8',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: 'PO4DL3',
    serialNumber: 'PO4DL3',
    routeId: 'DMES-R8',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: 'PO5DL2',
    serialNumber: 'PO5DL2',
    routeId: 'DMES-R8',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
  {
    id: 'PO5DL3',
    serialNumber: 'PO5DL3',
    routeId: 'DMES-R8',
    quantity: 1,
    plannedCompletionDate: '10/04/2024',
    releasedDate: '10/04/2024',
    releaseDate: '04/01/2024',
    status: 'IN_PROGRESS',
    progress: 0,
  },
];

// Mock Queue for home page
export const queueOrders = [
  { id: 'P02-BLK1', releaseDate: '04/01/2024' },
  { id: 'PO03-BLK2', releaseDate: '04/01/2024' },
  { id: 'PO4DL3', releaseDate: '04/01/2024' },
  { id: 'PO5DL2', releaseDate: '04/01/2024' },
  { id: 'PO5DL3', releaseDate: '04/01/2024' },
];

// Mock Production Lines with Orders
export const productionLines: ProductionLine[] = [
  {
    id: 'DL2',
    name: 'DL2',
    shift: '1/2',
    lateStatus: 'Late',
    orders: [
      { id: '1', orderId: 'PO4DL2', quantity: 51000, progress: 0, status: 'Late', workersCount: 0 },
      { id: '2', orderId: 'PO3DL2', quantity: 52000, progress: 0, status: 'Late', workersCount: 0 },
    ],
  },
  {
    id: 'BLK1',
    name: 'BLK1',
    shift: '1/2',
    lateStatus: 'Late',
    orders: [
      { id: '3', orderId: 'P01 BLK1', quantity: 51000, progress: 6, status: 'Late', workersCount: 0 },
      { id: '4', orderId: 'P01 BLK1', quantity: 52000, progress: 6, status: 'On Time', workersCount: 0 },
      { id: '5', orderId: '', quantity: 53000, progress: 0, status: 'On Time', workersCount: 0 },
    ],
  },
  {
    id: 'BLK2',
    name: 'BLK2',
    shift: '1/2',
    lateStatus: 'Late',
    orders: [
      { id: '6', orderId: 'PO01-BLK2', quantity: 51000, progress: 0, status: 'Late', workersCount: 0 },
      { id: '7', orderId: '', quantity: 53000, progress: 25, status: 'On Time', workersCount: 0 },
    ],
  },
  {
    id: 'BLK3',
    name: 'BLK3',
    shift: '1/2',
    lateStatus: 'Late',
    orders: [
      { id: '8', orderId: '1013/15', quantity: 51000, progress: 0, status: 'Late', workersCount: 0 },
      { id: '9', orderId: '', quantity: 54000, progress: 0, status: 'On Time', workersCount: 0 },
      { id: '10', orderId: '', quantity: 55000, progress: 0, status: 'On Time', workersCount: 0 },
      { id: '11', orderId: 'No Order', quantity: 57000, progress: 0, status: 'On Time', workersCount: 0 },
      { id: '12', orderId: 'No Order', quantity: 58000, progress: 0, status: 'On Time', workersCount: 0 },
      { id: '13', orderId: 'No Order', quantity: 59000, progress: 0, status: 'On Time', workersCount: 0 },
    ],
  },
  {
    id: 'DL3',
    name: 'DL3',
    shift: '1/2',
    lateStatus: 'Late',
    orders: [
      { id: '14', orderId: 'PO3DL3', quantity: 51000, progress: 0, status: 'Late', workersCount: 0 },
      { id: '15', orderId: 'PV2DL3', quantity: 52000, progress: 0, status: 'On Time', workersCount: 0 },
    ],
  },
  {
    id: 'DL4',
    name: 'DL4',
    shift: '1/2',
    orders: [
      { id: '16', orderId: '36082024', quantity: 51000, progress: 0, status: 'On Time', workersCount: 0 },
      { id: '17', orderId: '35082024', quantity: 52000, progress: 100, status: 'Completed', workersCount: 0 },
      { id: '18', orderId: '', quantity: 53000, progress: 60, status: 'On Time', workersCount: 0 },
    ],
  },
];

// Mock Operations
export const operations: Operation[] = [
  {
    id: 'OP_110000',
    productionOrderId: 'P02-BLK1',
    productionLine: 'BLK1',
    workstation: '3000',
    remainingTime: '0h 0m',
    progress: 0,
    status: 'Ready',
    timing: 'On time',
  },
  {
    id: 'OP_110003',
    productionOrderId: 'P02-BLK1',
    productionLine: 'BLK1',
    workstation: '2000',
    remainingTime: '0h 0m',
    progress: 0,
    status: 'Ready',
    timing: 'On time',
  },
  {
    id: 'OP_110020',
    productionOrderId: 'P02-BLK1',
    productionLine: 'BLK1',
    workstation: '2000',
    remainingTime: '0h 0m',
    progress: 0,
    status: 'Ready',
    timing: 'On time',
  },
];

// Mock Routes
export const routes: Route[] = [
  {
    id: 'HAL-X002',
    name: 'HAL-X002',
    lastUpdated: '06/04/2024',
    status: 'Active',
  },
  {
    id: 'DMES-R4',
    name: 'DMES-R4',
    lastUpdated: '06/05/2024',
    status: 'Inactive',
  },
  {
    id: 'X-H1-B1-2_1-3',
    name: 'X-H1-B1-2_1-3',
    lastUpdated: '06/05/2024',
    status: 'Inactive',
  },
  {
    id: 'HAL-X003',
    name: 'HAL-X003',
    lastUpdated: '06/05/2024',
    status: 'Active',
  },
];