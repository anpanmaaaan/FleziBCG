import { useEffect, useId, useRef, type ReactNode, type RefObject } from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";

interface DialogProps {
  open: boolean;
  onClose: () => void;
  titleId?: string;
  children: ReactNode;
  closeOnBackdrop?: boolean;
  initialFocusRef?: RefObject<HTMLElement>;
}

function getFirstFocusable(container: HTMLElement | null): HTMLElement | null {
  if (!container) {
    return null;
  }

  return container.querySelector<HTMLElement>(
    "button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])"
  );
}

export function Dialog({
  open,
  onClose,
  titleId,
  children,
  closeOnBackdrop = true,
  initialFocusRef,
}: DialogProps) {
  const autoId = useId();
  const resolvedTitleId = titleId ?? `dialog-title-${autoId}`;
  const contentRef = useRef<HTMLDivElement | null>(null);
  const previousActiveElementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (open) {
      previousActiveElementRef.current =
        document.activeElement instanceof HTMLElement ? document.activeElement : null;
    }
  }, [open]);

  return (
    <DialogPrimitive.Root open={open} onOpenChange={(nextOpen) => !nextOpen && onClose()}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay
          className="fixed inset-0 z-50 bg-black/40"
          onClick={closeOnBackdrop ? onClose : undefined}
        />
        <DialogPrimitive.Content
          ref={contentRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={resolvedTitleId}
          className="fixed left-1/2 top-1/2 z-50 w-full max-w-[95vw] -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white p-6 shadow-2xl sm:w-96"
          onEscapeKeyDown={onClose}
          onPointerDownOutside={(event) => {
            if (!closeOnBackdrop) {
              event.preventDefault();
            }
          }}
          onOpenAutoFocus={(event) => {
            event.preventDefault();
            if (initialFocusRef?.current) {
              initialFocusRef.current.focus();
              return;
            }
            const firstFocusable = getFirstFocusable(contentRef.current);
            firstFocusable?.focus();
          }}
          onCloseAutoFocus={(event) => {
            event.preventDefault();
            previousActiveElementRef.current?.focus();
          }}
        >
          {children}
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
