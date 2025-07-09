
import { tool } from "ai";
import { getDepartmentLevelStatisticsTermsDataSchema } from "./aitm.schema.ts";
import { getDepartmentLevelStatisticsTerms, GetDepartmentLevelStatisticsTermsData } from "..";

export default tool({
  description: `
  Get department-level statistics
Returns numeric statistics about the department and term (or
filter).

Shares the same variations on endpoint as the participation data.
    `,
  parameters: getDepartmentLevelStatisticsTermsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetDepartmentLevelStatisticsTermsData, "url"> ) => {
    try {
      const { data } = await getDepartmentLevelStatisticsTerms(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    