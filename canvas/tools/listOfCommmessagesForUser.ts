
import { tool } from "ai";
import { listOfCommmessagesForUserDataSchema } from "./aitm.schema.ts";
import { listOfCommmessagesForUser, ListOfCommmessagesForUserData } from "..";

export default tool({
  description: `
  List of CommMessages for a user
Retrieve a paginated list of messages sent to a user.
    `,
  parameters: listOfCommmessagesForUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListOfCommmessagesForUserData, "url"> ) => {
    try {
      const { data } = await listOfCommmessagesForUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    