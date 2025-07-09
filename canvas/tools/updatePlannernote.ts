
import { tool } from "ai";
import { updatePlannernoteDataSchema } from "./aitm.schema.ts";
import { updatePlannernote, UpdatePlannernoteData } from "..";

export default tool({
  description: `
  Update a PlannerNote
Update a planner note for the current user
    `,
  parameters: updatePlannernoteDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdatePlannernoteData, "url"> ) => {
    try {
      const { data } = await updatePlannernote(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    