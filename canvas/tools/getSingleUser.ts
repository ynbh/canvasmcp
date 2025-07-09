
import { tool } from "ai";
import { getSingleUserDataSchema } from "./aitm.schema.ts";
import { getSingleUser, GetSingleUserData } from "..";

export default tool({
  description: `
  Get single user
Return information on a single user.

Accepts the same include[] parameters as the
:users: action, and returns a
single user with the same fields as that action.
    `,
  parameters: getSingleUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleUserData, "url"> ) => {
    try {
      const { data } = await getSingleUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    