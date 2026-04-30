import { useEffect, useMemo, useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "./ui/dialog";
import { GripVertical, Eye, EyeOff } from "lucide-react";
import { useI18n } from "@/app/i18n";

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
  const { t } = useI18n();
  const [editedColumns, setEditedColumns] = useState<ColumnConfig[]>(columns);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  useEffect(() => {
    if (open) {
      setEditedColumns(columns);
    }
  }, [open, columns]);

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
  const hiddenCount = editedColumns.length - visibleCount;

  const orderedColumns = useMemo(
    () => [...editedColumns].sort((a, b) => a.order - b.order),
    [editedColumns],
  );

  const getColumnLabel = (column: ColumnConfig) => {
    const key = `poList.col.${column.id}`;
    return t(key as never, column.label);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl border-gray-200 bg-white p-0 shadow-xl">
        <div className="border-b border-gray-200 px-6 py-4">
          <DialogTitle>{t("poList.columns.dialog.title")}</DialogTitle>
          <DialogDescription className="mt-1">
            {t("poList.columns.dialog.description")}
          </DialogDescription>
        </div>

        <div className="space-y-4 px-6 py-5">
          <div className="grid gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm text-gray-700 md:grid-cols-2">
            <div className="rounded-md border border-green-200 bg-green-50 px-3 py-2">
              <span className="font-semibold text-green-700">{visibleCount}</span>
              <span className="ml-2">{t("poList.columns.dialog.summary.visible")}</span>
            </div>
            <div className="rounded-md border border-gray-200 bg-white px-3 py-2">
              <span className="font-semibold text-gray-700">{hiddenCount}</span>
              <span className="ml-2">{t("poList.columns.dialog.summary.hidden")}</span>
            </div>
          </div>

          <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-3 py-2">
            <div className="text-sm text-gray-600">
              <span className="font-semibold text-gray-900">{visibleCount}</span>
              <span className="mx-1">/</span>
              <span className="font-semibold text-gray-900">{editedColumns.length}</span>
              <span className="ml-2">{t("poList.columns.dialog.summary.total")}</span>
            </div>
            <button
              type="button"
              onClick={handleReset}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
            >
              {t("poList.columns.dialog.action.reset")}
            </button>
          </div>

          <div className="max-h-96 space-y-2 overflow-y-auto rounded-lg border border-gray-200 bg-white p-2">
            {orderedColumns.map((column, index) => (
              <div
                key={column.id}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
                className={`flex items-center gap-3 rounded-lg border p-3 transition-colors ${
                  draggedIndex === index ? 'opacity-50 bg-blue-50' : ''
                } ${!column.visible ? 'opacity-70' : ''} ${column.visible ? 'border-blue-200 bg-blue-50/40' : 'border-gray-200 bg-white hover:bg-gray-50'}`}
              >
                <GripVertical className="h-5 w-5 flex-shrink-0 text-gray-400" />
                
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{getColumnLabel(column)}</div>
                  <div className="text-xs text-gray-500">
                    {t("poList.columns.dialog.meta.id", { id: column.id })}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-600 min-w-[88px] text-center">
                    {t("poList.columns.dialog.meta.position", { position: column.order + 1 })}
                  </span>
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${column.visible ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
                    {column.visible ? t("poList.columns.dialog.state.visible") : t("poList.columns.dialog.state.hidden")}
                  </span>
                  <button
                    type="button"
                    onClick={() => toggleVisibility(column.id)}
                    className={`rounded-md border p-2 transition-colors ${
                      column.visible ? 'text-blue-600' : 'text-gray-400'
                    } hover:bg-gray-100`}
                    aria-label={column.visible ? t("poList.columns.dialog.aria.hide", { label: getColumnLabel(column) }) : t("poList.columns.dialog.aria.show", { label: getColumnLabel(column) })}
                  >
                    {column.visible ? (
                      <Eye className="h-5 w-5" />
                    ) : (
                      <EyeOff className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3">
            <p className="text-sm text-blue-800">
              <strong>{t("poList.columns.dialog.tip.title")}</strong> {t("poList.columns.dialog.tip.body")}
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-gray-200 px-6 py-4">
          <button
            type="button"
            onClick={() => onOpenChange(false)}
            className="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
          >
            {t("poList.columns.dialog.action.cancel")}
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="rounded-md bg-brand-cta px-4 py-2 text-white hover:bg-brand-cta-hover"
          >
            {t("poList.columns.dialog.action.done")}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}