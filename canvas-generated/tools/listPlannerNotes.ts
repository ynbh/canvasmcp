
import { tool } from "ai";
import { listPlannerNotesDataSchema } from "./aitm.schema.ts";
import { listPlannerNotes, ListPlannerNotesData } from "..";

export default tool({
  description: `
  List planner notes
Retrieve the paginated list of planner notes

Retrieve planner note for a user
    `,
  parameters: listPlannerNotesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPlannerNotesData, "url"> ) => {
    try {
      const { data } = await listPlannerNotes(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    