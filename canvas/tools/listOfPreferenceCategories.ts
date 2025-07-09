
import { tool } from "ai";
import { listOfPreferenceCategoriesDataSchema } from "./aitm.schema.ts";
import { listOfPreferenceCategories, ListOfPreferenceCategoriesData } from "..";

export default tool({
  description: `
  List of preference categories
Fetch all notification preference categories for the given
communication channel
    `,
  parameters: listOfPreferenceCategoriesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListOfPreferenceCategoriesData, "url"> ) => {
    try {
      const { data } = await listOfPreferenceCategories(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    