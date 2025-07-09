
import { tool } from "ai";
import { showPlannernoteDataSchema } from "./aitm.schema.ts";
import { showPlannernote, ShowPlannernoteData } from "..";

export default tool({
  description: `
  Show a PlannerNote
Retrieve a planner note for the current user
    `,
  parameters: showPlannernoteDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowPlannernoteData, "url"> ) => {
    try {
      const { data } = await showPlannernote(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    