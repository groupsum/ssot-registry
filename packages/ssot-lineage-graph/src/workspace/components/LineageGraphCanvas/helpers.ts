import { LineageNode, GraphViewMode } from "../../types";

// Generate perpendicular offsets on bezier curves or straight lines for parallel double-edges
export function generateGhostParallelPaths(
  startX: number,
  startY: number,
  endX: number,
  endY: number,
  mode: string,
  offset: number
): string {
  if (mode === "lineage" || mode === "proof" || mode === "packs") {
    const midX = (startX + endX) / 2;
    return `M ${startX} ${startY + offset} C ${midX} ${startY + offset}, ${midX} ${endY + offset}, ${endX} ${endY + offset}`;
  }
  
  // Straight line normal factor translation for force layouts
  const dx = endX - startX;
  const dy = endY - startY;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const nx = -dy / len; 
  const ny = dx / len;
  
  const ox = nx * offset;
  const oy = ny * offset;
  
  return `M ${startX + ox} ${startY + oy} L ${endX + ox} ${endY + oy}`;
}

// Node helper signals for specific statuses in modes
export const getNodeBadgeClass = (node: LineageNode, mode: GraphViewMode) => {
  if (mode === "validation") {
    switch (node.validation?.status) {
      case "fail":
        return "bg-rose-500 text-white animate-pulse";
      case "warn":
        return "bg-orange-400 text-white";
      default:
        return "bg-emerald-500 text-white";
    }
  }
  if (mode === "proof") {
    if (node.proof?.testStatus === "failed") return "bg-rose-500 text-white";
    if (node.proof?.testStatus === "passed") return "bg-indigo-500 text-white";
  }
  return "";
};

export const getNodeBadgeInfo = (node: LineageNode, mode: GraphViewMode) => {
  // Determine status precisely based on view mode first, fallback to generic props next
  if (mode === "validation") {
    switch (node.validation?.status) {
      case "fail":
        return {
          className: "bg-rose-500 text-white animate-pulse",
          icon: "fail",
          label: "ValidationError"
        };
      case "warn":
        return {
          className: "bg-amber-500 text-white",
          icon: "warn",
          label: "Warning"
        };
      default:
        return {
          className: "bg-emerald-500 text-white",
          icon: "verified",
          label: "Verified Proof"
        };
    }
  }

  if (mode === "proof") {
    if (node.proof?.testStatus === "failed") {
      return {
        className: "bg-rose-500 text-white animate-pulse",
        icon: "fail",
        label: "ValidationError"
      };
    }
    if (node.proof?.testStatus === "passed") {
      return {
        className: "bg-indigo-500 text-white",
        icon: "pass",
        label: "Active Layer Node"
      };
    }
  }

  // Generic fallbacks across all other modes so the legend is always active and correct
  if (node.validation?.status === "fail" || node.proof?.testStatus === "failed") {
    return {
      className: "bg-rose-500 text-white animate-pulse",
      icon: "fail",
      label: "ValidationError"
    };
  }
  if (node.proof?.testStatus === "passed") {
    return {
      className: "bg-indigo-500 text-white",
      icon: "pass",
      label: "Active Layer Node"
    };
  }
  if (node.validation?.status === "pass" || node.status === "certified") {
    return {
      className: "bg-emerald-500 text-white",
      icon: "verified",
      label: "Verified Proof"
    };
  }
  if (node.validation?.status === "warn") {
    return {
      className: "bg-amber-500 text-white",
      icon: "warn",
      label: "Warning"
    };
  }

  return null;
};

export const getFamilySvgColor = (family: string): string => {
  switch (family) {
    case "ADR": return "#d97706";
    case "Spec": return "#2563eb";
    case "SPEC": return "#2563eb";
    case "Feature": return "#4f46e5";
    case "Claim": return "#9333ea";
    case "Test": return "#e11d48";
    case "Evidence": return "#059669";
    case "Release": return "#0d9488";
    case "Boundary": return "#475569";
    case "Risk": return "#ea580c";
    case "Issue": return "#dc2626";
    default: return "#4b5563";
  }
};
