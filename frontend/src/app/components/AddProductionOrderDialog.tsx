import { useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "./ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Calendar } from "./ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { Calendar as CalendarIcon, Upload, Loader2, CheckCircle2, RefreshCw, Search } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

interface AddProductionOrderDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: any) => void;
}

interface SAPOrder {
  sapOrderId: string;
  serialNumber: string;
  lotId: string;
  customer: string;
  productName: string;
  materialCode: string;
  routeId: string;
  priority: 'High' | 'Medium' | 'Low';
  quantity: number;
  plannedStartDate: string;
  dueDate: string;
  releaseDate: string;
  assignee: string;
  department: string;
}

// Mock SAP Orders
const MOCK_SAP_ORDERS: SAPOrder[] = [
  {
    sapOrderId: "SAP-1000245",
    serialNumber: "SN-2026-001",
    lotId: "LOT-2026-A001",
    customer: "Toyota Vietnam",
    productName: "Engine Block A-2024",
    materialCode: "MAT-ENG-A2024",
    routeId: "DMES-R1",
    priority: "High",
    quantity: 5000,
    plannedStartDate: "03/24/2026",
    dueDate: "03/30/2026",
    releaseDate: "03/23/2026",
    assignee: "Nguyen Van A",
    department: "Production Dept A",
  },
  {
    sapOrderId: "SAP-1000246",
    serialNumber: "SN-2026-002",
    lotId: "LOT-2026-A002",
    customer: "Honda Vietnam",
    productName: "Transmission Unit B-2024",
    materialCode: "MAT-TRA-B2024",
    routeId: "DMES-R8",
    priority: "High",
    quantity: 3000,
    plannedStartDate: "03/25/2026",
    dueDate: "04/05/2026",
    releaseDate: "03/23/2026",
    assignee: "Tran Thi B",
    department: "Production Dept B",
  },
  {
    sapOrderId: "SAP-1000247",
    serialNumber: "SN-2026-003",
    lotId: "LOT-2026-B001",
    customer: "Samsung Vietnam",
    productName: "Cylinder Head C-2024",
    materialCode: "MAT-CYL-C2024",
    routeId: "DMES-R11",
    priority: "Medium",
    quantity: 8000,
    plannedStartDate: "03/26/2026",
    dueDate: "04/10/2026",
    releaseDate: "03/23/2026",
    assignee: "Le Van C",
    department: "Production Dept C",
  },
  {
    sapOrderId: "SAP-1000248",
    serialNumber: "SN-2026-004",
    lotId: "LOT-2026-B002",
    customer: "LG Electronics",
    productName: "Bearing Housing D-2024",
    materialCode: "MAT-BEA-D2024",
    routeId: "DMES-R1",
    priority: "Medium",
    quantity: 4500,
    plannedStartDate: "03/27/2026",
    dueDate: "04/08/2026",
    releaseDate: "03/23/2026",
    assignee: "Pham Thi D",
    department: "Production Dept A",
  },
  {
    sapOrderId: "SAP-1000249",
    serialNumber: "SN-2026-005",
    lotId: "LOT-2026-C001",
    customer: "Panasonic Vietnam",
    productName: "Valve Assembly E-2024",
    materialCode: "MAT-VAL-E2024",
    routeId: "HAL-X002",
    priority: "Low",
    quantity: 2000,
    plannedStartDate: "03/28/2026",
    dueDate: "04/15/2026",
    releaseDate: "03/23/2026",
    assignee: "Hoang Van E",
    department: "Production Dept D",
  },
  {
    sapOrderId: "SAP-1000250",
    serialNumber: "SN-2026-006",
    lotId: "LOT-2026-C002",
    customer: "Toyota Vietnam",
    productName: "Crankshaft F-2024",
    materialCode: "MAT-CRA-F2024",
    routeId: "DMES-R8",
    priority: "High",
    quantity: 6000,
    plannedStartDate: "03/24/2026",
    dueDate: "03/31/2026",
    releaseDate: "03/23/2026",
    assignee: "Nguyen Thi F",
    department: "Production Dept B",
  },
];

export function AddProductionOrderDialog({ open, onOpenChange, onSubmit }: AddProductionOrderDialogProps) {
  const [activeTab, setActiveTab] = useState("erp");
  
  // Manual Entry State
  const [formData, setFormData] = useState({
    serialNumber: "",
    lotId: "",
    customer: "",
    productName: "",
    routeId: "",
    priority: "",
    machineNumber: "",
    quantity: "",
    plannedStartDate: undefined as Date | undefined,
    plannedCompletionDate: undefined as Date | undefined,
    releaseDate: undefined as Date | undefined,
    assignee: "",
    department: "",
    materialCode: "",
  });

  // ERP Integration State
  const [sapOrders, setSapOrders] = useState<SAPOrder[]>([]);
  const [selectedOrders, setSelectedOrders] = useState<Set<string>>(new Set());
  const [isSyncingSAP, setIsSyncingSAP] = useState(false);
  const [sapSearchTerm, setSapSearchTerm] = useState("");
  const [sapFilterPriority, setSapFilterPriority] = useState("");
  const [sapFilterCustomer, setSapFilterCustomer] = useState("");

  // File Upload State
  const [isImportingFile, setIsImportingFile] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const resetForm = () => {
    setFormData({
      serialNumber: "",
      lotId: "",
      customer: "",
      productName: "",
      routeId: "",
      priority: "",
      machineNumber: "",
      quantity: "",
      plannedStartDate: undefined,
      plannedCompletionDate: undefined,
      releaseDate: undefined,
      assignee: "",
      department: "",
      materialCode: "",
    });
    setSelectedFile(null);
    setSelectedOrders(new Set());
    setSapOrders([]);
    setSapSearchTerm("");
    setSapFilterPriority("");
    setSapFilterCustomer("");
  };

  // Manual Entry Submit
  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      plannedStartDate: formData.plannedStartDate?.toLocaleDateString('en-US'),
      plannedCompletionDate: formData.plannedCompletionDate?.toLocaleDateString('en-US'),
      releaseDate: formData.releaseDate?.toLocaleDateString('en-US'),
    });
    resetForm();
    onOpenChange(false);
  };

  // SAP Sync
  const handleSAPSync = async () => {
    setIsSyncingSAP(true);
    
    setTimeout(() => {
      setSapOrders(MOCK_SAP_ORDERS);
      setIsSyncingSAP(false);
      toast.success(`Đã tải ${MOCK_SAP_ORDERS.length} production orders từ SAP ERP`);
    }, 2000);
  };

  // Filter SAP Orders
  const filteredSapOrders = sapOrders.filter(order => {
    const matchesSearch = 
      order.sapOrderId.toLowerCase().includes(sapSearchTerm.toLowerCase()) ||
      order.serialNumber.toLowerCase().includes(sapSearchTerm.toLowerCase()) ||
      order.customer.toLowerCase().includes(sapSearchTerm.toLowerCase()) ||
      order.productName.toLowerCase().includes(sapSearchTerm.toLowerCase());
    
    const matchesPriority = !sapFilterPriority || order.priority === sapFilterPriority;
    const matchesCustomer = !sapFilterCustomer || order.customer === sapFilterCustomer;

    return matchesSearch && matchesPriority && matchesCustomer;
  });

  // Toggle Order Selection
  const toggleOrderSelection = (orderId: string) => {
    const newSelected = new Set(selectedOrders);
    if (newSelected.has(orderId)) {
      newSelected.delete(orderId);
    } else {
      newSelected.add(orderId);
    }
    setSelectedOrders(newSelected);
  };

  // Select All
  const handleSelectAll = () => {
    if (selectedOrders.size === filteredSapOrders.length) {
      setSelectedOrders(new Set());
    } else {
      setSelectedOrders(new Set(filteredSapOrders.map(o => o.sapOrderId)));
    }
  };

  // Import Selected SAP Orders
  const handleImportSAPOrders = () => {
    const ordersToImport = sapOrders.filter(o => selectedOrders.has(o.sapOrderId));
    
    ordersToImport.forEach((order, index) => {
      // Add delay between each import to ensure unique timestamps
      setTimeout(() => {
        onSubmit({
          serialNumber: order.serialNumber,
          lotId: order.lotId,
          customer: order.customer,
          productName: order.productName,
          materialCode: order.materialCode,
          routeId: order.routeId,
          priority: order.priority,
          quantity: order.quantity.toString(),
          plannedStartDate: order.plannedStartDate,
          plannedCompletionDate: order.dueDate,
          releaseDate: order.releaseDate,
          assignee: order.assignee,
          department: order.department,
        });
      }, index * 10); // 10ms delay between each order
    });

    toast.success(`Đang import ${ordersToImport.length} production orders từ SAP...`);
    
    // Close dialog after last order is imported
    setTimeout(() => {
      resetForm();
      onOpenChange(false);
    }, ordersToImport.length * 10 + 100);
  };

  // File Upload - Fill form with data
  const handleFileImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setIsImportingFile(true);

    setTimeout(() => {
      // Simulate parsing first row of Excel/CSV and fill the form
      const parsedData = {
        serialNumber: `FILE-SN-${Date.now()}`,
        lotId: `LOT-FILE-${Date.now()}`,
        customer: "Mitsubishi Vietnam",
        productName: "Piston Ring G-2024",
        materialCode: "MAT-PIS-G2024",
        routeId: "DMES-R11",
        priority: "High",
        quantity: "7000",
        plannedStartDate: new Date(),
        plannedCompletionDate: new Date(Date.now() + 12 * 24 * 60 * 60 * 1000),
        releaseDate: new Date(),
        assignee: "Vu Thi G",
        department: "Production Dept C",
      };
      
      setFormData(parsedData);
      setIsImportingFile(false);
      toast.success(`Đã load dữ liệu từ file "${file.name}" vào form`);
    }, 1500);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'text-red-600 bg-red-50';
      case 'Medium': return 'text-yellow-600 bg-yellow-50';
      case 'Low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const uniqueCustomers = Array.from(new Set(sapOrders.map(o => o.customer)));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] max-h-[95vh] overflow-hidden flex flex-col">
        <DialogTitle>Add Production Order</DialogTitle>
        <DialogDescription>
          Sync từ ERP hoặc nhập thủ công
        </DialogDescription>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="erp">ERP Integration</TabsTrigger>
            <TabsTrigger value="manual">Manual Entry</TabsTrigger>
          </TabsList>

          {/* ERP Integration Tab */}
          <TabsContent value="erp" className="flex-1 flex flex-col overflow-hidden mt-4">
            <div className="flex-1 flex flex-col space-y-4 overflow-auto">
              {/* Sync Button */}
              {sapOrders.length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed rounded-lg">
                  <RefreshCw className="w-16 h-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Sync Production Orders từ SAP ERP</h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Kết nối với SAP ERP để tải danh sách production orders
                  </p>
                  <button
                    onClick={handleSAPSync}
                    disabled={isSyncingSAP}
                    className="flex items-center gap-2 px-6 py-3 bg-[#33B2C1] text-white rounded-lg hover:bg-[#2a9aa8] disabled:opacity-50"
                  >
                    {isSyncingSAP ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Đang sync...</span>
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-5 h-5" />
                        <span>Sync from SAP</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Orders Table */}
              {sapOrders.length > 0 && (
                <>
                  {/* Filters */}
                  <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1 relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <Input
                        placeholder="Search by Order ID, Serial, Customer, Product..."
                        value={sapSearchTerm}
                        onChange={(e) => setSapSearchTerm(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                    <Select value={sapFilterPriority} onValueChange={setSapFilterPriority}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="Priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value=" ">All Priority</SelectItem>
                        <SelectItem value="High">High</SelectItem>
                        <SelectItem value="Medium">Medium</SelectItem>
                        <SelectItem value="Low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={sapFilterCustomer} onValueChange={setSapFilterCustomer}>
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Customer" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value=" ">All Customers</SelectItem>
                        {uniqueCustomers.map(customer => (
                          <SelectItem key={customer} value={customer}>{customer}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <button
                      onClick={handleSAPSync}
                      disabled={isSyncingSAP}
                      className="px-3 py-2 border rounded hover:bg-white"
                      title="Refresh"
                    >
                      <RefreshCw className={`w-4 h-4 ${isSyncingSAP ? 'animate-spin' : ''}`} />
                    </button>
                  </div>

                  {/* Selection Info */}
                  <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">
                        {selectedOrders.size} / {filteredSapOrders.length} orders selected
                      </span>
                    </div>
                    <button
                      onClick={handleSelectAll}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      {selectedOrders.size === filteredSapOrders.length ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>

                  {/* Table - Scrollable Area */}
                  <div className="border rounded-lg overflow-hidden">
                    <div className="overflow-auto max-h-[400px]">
                      <table className="w-full">
                        <thead className="bg-gray-50 border-b sticky top-0">
                          <tr>
                            <th className="px-4 py-3 text-left w-12">
                              <input
                                type="checkbox"
                                checked={selectedOrders.size === filteredSapOrders.length && filteredSapOrders.length > 0}
                                onChange={handleSelectAll}
                                className="w-4 h-4"
                              />
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">SAP Order ID</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">Serial / LOT</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">Customer</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">Product</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">Priority</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">Quantity</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold">Due Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredSapOrders.map((order, index) => (
                            <tr 
                              key={order.sapOrderId}
                              className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 cursor-pointer`}
                              onClick={() => toggleOrderSelection(order.sapOrderId)}
                            >
                              <td className="px-4 py-3">
                                <input
                                  type="checkbox"
                                  checked={selectedOrders.has(order.sapOrderId)}
                                  onChange={() => toggleOrderSelection(order.sapOrderId)}
                                  className="w-4 h-4"
                                  onClick={(e) => e.stopPropagation()}
                                />
                              </td>
                              <td className="px-4 py-3">
                                <div className="font-medium">{order.sapOrderId}</div>
                                <div className="text-xs text-gray-500">{order.routeId}</div>
                              </td>
                              <td className="px-4 py-3">
                                <div className="text-sm">{order.serialNumber}</div>
                                <div className="text-xs text-gray-500">{order.lotId}</div>
                              </td>
                              <td className="px-4 py-3 text-sm">{order.customer}</td>
                              <td className="px-4 py-3">
                                <div className="text-sm">{order.productName}</div>
                                <div className="text-xs text-gray-500">{order.materialCode}</div>
                              </td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(order.priority)}`}>
                                  {order.priority}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-sm">{order.quantity.toLocaleString()}</td>
                              <td className="px-4 py-3 text-sm">{order.dueDate}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </div>
          </TabsContent>

          {/* Manual Entry Tab */}
          <TabsContent value="manual" className="flex-1 overflow-y-auto mt-4">
            <form onSubmit={handleManualSubmit} className="space-y-4">
              {/* File Upload Button */}
              <div className="p-4 bg-gray-50 border-2 border-dashed rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold mb-1">Import từ Excel/CSV File</h4>
                    <p className="text-sm text-gray-500">
                      Upload file để tự động điền các trường thông tin
                    </p>
                  </div>
                  <div>
                    <input
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      onChange={handleFileImport}
                      className="hidden"
                      id="manual-file-upload"
                      disabled={isImportingFile}
                    />
                    <label
                      htmlFor="manual-file-upload"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 cursor-pointer"
                    >
                      {isImportingFile ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Đang xử lý...</span>
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4" />
                          <span>Upload File</span>
                        </>
                      )}
                    </label>
                  </div>
                </div>
                {selectedFile && (
                  <div className="mt-3 flex items-center gap-2 text-sm text-green-600">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Đã load dữ liệu từ: <strong>{selectedFile.name}</strong></span>
                  </div>
                )}
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="serialNumber">Serial Number *</Label>
                  <Input
                    id="serialNumber"
                    value={formData.serialNumber}
                    onChange={(e) => setFormData(prev => ({ ...prev, serialNumber: e.target.value }))}
                    required
                    placeholder="Enter serial number"
                  />
                </div>

                <div>
                  <Label htmlFor="lotId">LOT ID</Label>
                  <Input
                    id="lotId"
                    value={formData.lotId}
                    onChange={(e) => setFormData(prev => ({ ...prev, lotId: e.target.value }))}
                    placeholder="Enter LOT ID"
                  />
                </div>

                <div>
                  <Label htmlFor="customer">Customer</Label>
                  <Input
                    id="customer"
                    value={formData.customer}
                    onChange={(e) => setFormData(prev => ({ ...prev, customer: e.target.value }))}
                    placeholder="Customer name"
                  />
                </div>

                <div>
                  <Label htmlFor="productName">Product Name</Label>
                  <Input
                    id="productName"
                    value={formData.productName}
                    onChange={(e) => setFormData(prev => ({ ...prev, productName: e.target.value }))}
                    placeholder="Product name"
                  />
                </div>

                <div>
                  <Label htmlFor="routeId">Route ID *</Label>
                  <Select
                    value={formData.routeId}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, routeId: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select route" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DMES-R1">DMES-R1</SelectItem>
                      <SelectItem value="DMES-R8">DMES-R8</SelectItem>
                      <SelectItem value="DMES-R11">DMES-R11</SelectItem>
                      <SelectItem value="HAL-X002">HAL-X002</SelectItem>
                      <SelectItem value="HAL-X003">HAL-X003</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={formData.priority}
                    onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="High">High</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="Low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="machineNumber">Machine Number</Label>
                  <Input
                    id="machineNumber"
                    value={formData.machineNumber}
                    onChange={(e) => setFormData(prev => ({ ...prev, machineNumber: e.target.value }))}
                    placeholder="Optional"
                  />
                </div>

                <div>
                  <Label htmlFor="quantity">Quantity *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => setFormData(prev => ({ ...prev, quantity: e.target.value }))}
                    required
                    placeholder="Enter quantity"
                  />
                </div>

                <div>
                  <Label htmlFor="materialCode">Material Code</Label>
                  <Input
                    id="materialCode"
                    value={formData.materialCode}
                    onChange={(e) => setFormData(prev => ({ ...prev, materialCode: e.target.value }))}
                    placeholder="Material code"
                  />
                </div>

                <div>
                  <Label>Planned Start Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <button
                        type="button"
                        className="w-full flex items-center justify-between px-3 py-2 border rounded text-sm hover:bg-gray-50"
                      >
                        {formData.plannedStartDate ? (
                          format(formData.plannedStartDate, "MM/dd/yyyy")
                        ) : (
                          <span className="text-gray-400">Select date</span>
                        )}
                        <CalendarIcon className="w-4 h-4 text-gray-400" />
                      </button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.plannedStartDate}
                        onSelect={(date) => setFormData(prev => ({ ...prev, plannedStartDate: date }))}
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div>
                  <Label>Planned Completion Date *</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <button
                        type="button"
                        className="w-full flex items-center justify-between px-3 py-2 border rounded text-sm hover:bg-gray-50"
                      >
                        {formData.plannedCompletionDate ? (
                          format(formData.plannedCompletionDate, "MM/dd/yyyy")
                        ) : (
                          <span className="text-gray-400">Select date</span>
                        )}
                        <CalendarIcon className="w-4 h-4 text-gray-400" />
                      </button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.plannedCompletionDate}
                        onSelect={(date) => setFormData(prev => ({ ...prev, plannedCompletionDate: date }))}
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div>
                  <Label>Release Date *</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <button
                        type="button"
                        className="w-full flex items-center justify-between px-3 py-2 border rounded text-sm hover:bg-gray-50"
                      >
                        {formData.releaseDate ? (
                          format(formData.releaseDate, "MM/dd/yyyy")
                        ) : (
                          <span className="text-gray-400">Select date</span>
                        )}
                        <CalendarIcon className="w-4 h-4 text-gray-400" />
                      </button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.releaseDate}
                        onSelect={(date) => setFormData(prev => ({ ...prev, releaseDate: date }))}
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div>
                  <Label htmlFor="assignee">Assignee</Label>
                  <Input
                    id="assignee"
                    value={formData.assignee}
                    onChange={(e) => setFormData(prev => ({ ...prev, assignee: e.target.value }))}
                    placeholder="Person in charge"
                  />
                </div>

                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={formData.department}
                    onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
                    placeholder="Department"
                  />
                </div>
              </div>
            </form>
          </TabsContent>
        </Tabs>

        {/* Actions - Fixed Footer Outside Tabs */}
        <div className="flex justify-end gap-3 pt-4 border-t mt-4">
          <button
            type="button"
            onClick={() => {
              resetForm();
              onOpenChange(false);
            }}
            className="px-4 py-2 border rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          
          {activeTab === 'erp' && sapOrders.length > 0 && (
            <button
              onClick={handleImportSAPOrders}
              disabled={selectedOrders.size === 0}
              className="px-4 py-2 bg-[#33B2C1] text-white rounded hover:bg-[#2a9aa8] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Import {selectedOrders.size} Order{selectedOrders.size !== 1 ? 's' : ''}
            </button>
          )}
          
          {activeTab === 'manual' && (
            <button
              onClick={handleManualSubmit}
              className="px-4 py-2 bg-[#33B2C1] text-white rounded hover:bg-[#2a9aa8]"
            >
              Create Order
            </button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}