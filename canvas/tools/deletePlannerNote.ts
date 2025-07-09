
import { tool } from "ai";
import { deletePlannerNoteDataSchema } from "./aitm.schema.ts";
import { deletePlannerNote, DeletePlannerNoteData } from "..";

export default tool({
  description: `
  Delete a planner note
Delete a planner note for the current user
    `,
  parameters: deletePlannerNoteDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePlannerNoteData, "url"> ) => {
    try {
      const { data } = await deletePlannerNote(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    