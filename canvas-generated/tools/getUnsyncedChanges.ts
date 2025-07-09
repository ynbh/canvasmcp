
import { tool } from "ai";
import { getUnsyncedChangesDataSchema } from "./aitm.schema.ts";
import { getUnsyncedChanges, GetUnsyncedChangesData } from "..";

export default tool({
  description: `
  Get unsynced changes
Retrieve a list of learning objects that have changed since the last blueprint
sync operation.
    `,
  parameters: getUnsyncedChangesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetUnsyncedChangesData, "url"> ) => {
    try {
      const { data } = await getUnsyncedChanges(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    