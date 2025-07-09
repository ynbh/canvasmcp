
import { tool } from "ai";
import { updateAssignmentOverrideDataSchema } from "./aitm.schema.ts";
import { updateAssignmentOverride, UpdateAssignmentOverrideData } from "..";

export default tool({
  description: `
  Update an assignment override
All current overridden values must be supplied if they are to be
retained;
e.g. if due_at was overridden, but this PUT omits a value for due_at,
due_at will no
longer be overridden. If the override is adhoc and
student_ids is not supplied, the target override
set is unchanged. Target
override sets cannot be changed for group or section overrides.
    `,
  parameters: updateAssignmentOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateAssignmentOverrideData, "url"> ) => {
    try {
      const { data } = await updateAssignmentOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    