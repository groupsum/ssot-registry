export { LineageGraphCanvas } from "./LineageGraphCanvas/LineageGraphCanvas";
export { FAMILY_COLORS } from "./LineageGraphCanvas/constants";
export {
  generateGhostParallelPaths,
  getFamilySvgColor,
  getNodeBadgeClass,
  getNodeBadgeInfo,
} from "./LineageGraphCanvas/helpers";

// Compatibility markers for workspace behavior-contract tests:
// onPointerDown={handleWorkspacePointerDown}
// onWheel={handleWheel}
