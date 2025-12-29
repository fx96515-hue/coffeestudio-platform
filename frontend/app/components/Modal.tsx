"use client";

import { useEffect } from "react";

export type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
};

export default function Modal({ isOpen, onClose, title, children, size = "md" }: ModalProps) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = "hidden";
      document.addEventListener("keydown", handleKeyDown);
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizeStyles = {
    sm: { maxWidth: "28rem" },
    md: { maxWidth: "42rem" },
    lg: { maxWidth: "56rem" },
    xl: { maxWidth: "72rem" },
  } as const;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        right: 0,
        bottom: 0,
        left: 0,
        zIndex: 50,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
      }}
      onClick={onClose}
    >
      <div
        className="panel"
        style={{
          padding: "24px",
          width: "100%",
          maxHeight: "90vh",
          overflowY: "auto",
          ...sizeStyles[size],
        }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {title && (
          <div className="rowBetween" style={{ marginBottom: 16 }}>
            <h2 className="h2">{title}</h2>
            <button
              className="btn"
              onClick={onClose}
              style={{ padding: "6px 12px" }}
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>
        )}
        {children}
      </div>
    </div>
  );
}
