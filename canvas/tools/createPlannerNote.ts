
import { tool } from "ai";
import { createPlannerNoteDataSchema } from "./aitm.schema.ts";
import { createPlannerNote, CreatePlannerNoteData } from "..";

export default tool({
  description: `
  Create a planner note
Create a planner note for the current user
    `,
  parameters: createPlannerNoteDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreatePlannerNoteData, "url"> ) => {
    try {
      const { data } = await createPlannerNote(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    