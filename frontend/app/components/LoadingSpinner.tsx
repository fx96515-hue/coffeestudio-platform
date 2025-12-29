export default function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeMap = {
    sm: { width: 16, height: 16, borderWidth: 2 },
    md: { width: 32, height: 32, borderWidth: 3 },
    lg: { width: 48, height: 48, borderWidth: 4 },
  };

  const { width, height, borderWidth } = sizeMap[size];

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }} role="status" aria-label="Loading">
      <div
        style={{
          width,
          height,
          border: `${borderWidth}px solid rgba(87, 134, 255, 0.3)`,
          borderTop: `${borderWidth}px solid rgba(87, 134, 255, 0.9)`,
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }
        `
      }} />
    </div>
  );
}
