import { useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "./ui/dialog";
import { GripVertical, Eye, EyeOff } from "lucide-react";

export interface ColumnConfig {
  id: string;
  label: string;
  visible: boolean;
  order: number;
  width?: string;
}

interface ColumnManagerDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  columns: ColumnConfig[];
  onSave: (columns: ColumnConfig[]) => void;
}

export function ColumnManagerDialog({ open, onOpenChange, columns, onSave }: ColumnManagerDialogProps) {
  const [editedColumns, setEditedColumns] = useState<ColumnConfig[]>(columns);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newColumns = [...editedColumns];
    const draggedItem = newColumns[draggedIndex];
    newColumns.splice(draggedIndex, 1);
    newColumns.splice(index, 0, draggedItem);

    // Update order
    newColumns.forEach((col, idx) => {
      col.order = idx;
    });

    setEditedColumns(newColumns);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const toggleVisibility = (id: string) => {
    setEditedColumns(prev =>
      prev.map(col =>
        col.id === id ? { ...col, visible: !col.visible } : col
      )
    );
  };

  const handleSave = () => {
    onSave(editedColumns);
    onOpenChange(false);
  };

  const handleReset = () => {
    setEditedColumns(columns);
  };

  const visibleCount = editedColumns.filter(col => col.visible).length;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogTitle>Quản lý cột hiển thị</DialogTitle>
        <DialogDescription>
          Tùy chỉnh các cột hiển thị và sắp xếp thứ tự của chúng
        </DialogDescription>

        <div className="mt-4">
          <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm">
              <span className="font-semibold">{visibleCount}</span> / {editedColumns.length} cột đang hiển thị
            </div>
            <button
              onClick={handleReset}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Đặt lại mặc định
            </button>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {editedColumns.map((column, index) => (
              <div
                key={column.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
                className={`flex items-center gap-3 p-3 border rounded-lg cursor-move hover:bg-gray-50 transition-colors ${
                  draggedIndex === index ? 'opacity-50 bg-blue-50' : ''
                } ${!column.visible ? 'opacity-60' : ''}`}
              >
                <GripVertical className="w-5 h-5 text-gray-400 flex-shrink-0" />
                
                <div className="flex-1">
                  <div className="font-medium">{column.label}</div>
                  <div className="text-xs text-gray-500">ID: {column.id}</div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 min-w-[60px]">
                    Vị trí #{column.order + 1}
                  </span>
                  <button
                    onClick={() => toggleVisibility(column.id)}
                    className={`p-2 rounded hover:bg-gray-100 transition-colors ${
                      column.visible ? 'text-blue-600' : 'text-gray-400'
                    }`}
                  >
                    {column.visible ? (
                      <Eye className="w-5 h-5" />
                    ) : (
                      <EyeOff className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              💡 <strong>Hướng dẫn:</strong> Kéo thả để sắp xếp lại thứ tự cột. Click icon mắt để ẩn/hiện cột.
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={() => onOpenChange(false)}
            className="px-4 py-2 border rounded hover:bg-gray-50"
          >
            Hủy
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-[#33B2C1] text-white rounded hover:bg-[#2a9aa8]"
          >
            Lưu thay đổi
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}