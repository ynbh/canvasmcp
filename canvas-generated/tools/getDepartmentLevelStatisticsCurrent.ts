
import { tool } from "ai";
import { getDepartmentLevelStatisticsCurrentDataSchema } from "./aitm.schema.ts";
import { getDepartmentLevelStatisticsCurrent, GetDepartmentLevelStatisticsCurrentData } from "..";

export default tool({
  description: `
  Get department-level statistics
Returns numeric statistics about the department and term (or
filter).

Shares the same variations on endpoint as the participation data.
    `,
  parameters: getDepartmentLevelStatisticsCurrentDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetDepartmentLevelStatisticsCurrentData, "url"> ) => {
    try {
      const { data } = await getDepartmentLevelStatisticsCurrent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    