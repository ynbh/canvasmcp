
import { tool } from "ai";
import { getSingleGroupCategoryDataSchema } from "./aitm.schema.ts";
import { getSingleGroupCategory, GetSingleGroupCategoryData } from "..";

export default tool({
  description: `
  Get a single group category
Returns the data for a single group category, or a 401 if the caller
doesn't have
the rights to see it.
    `,
  parameters: getSingleGroupCategoryDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGroupCategoryData, "url"> ) => {
    try {
      const { data } = await getSingleGroupCategory(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    