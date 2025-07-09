
import { tool } from "ai";
import { listLicensesCoursesDataSchema } from "./aitm.schema.ts";
import { listLicensesCourses, ListLicensesCoursesData } from "..";

export default tool({
  description: `
  List licenses
A paginated list of licenses that can be applied
    `,
  parameters: listLicensesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLicensesCoursesData, "url"> ) => {
    try {
      const { data } = await listLicensesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    