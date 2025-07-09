
import { tool } from "ai";
import { getDepartmentLevelStatisticsCompletedDataSchema } from "./aitm.schema.ts";
import { getDepartmentLevelStatisticsCompleted, GetDepartmentLevelStatisticsCompletedData } from "..";

export default tool({
  description: `
  Get department-level statistics
Returns numeric statistics about the department and term (or
filter).

Shares the same variations on endpoint as the participation data.
    `,
  parameters: getDepartmentLevelStatisticsCompletedDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetDepartmentLevelStatisticsCompletedData, "url"> ) => {
    try {
      const { data } = await getDepartmentLevelStatisticsCompleted(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    