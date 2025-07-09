
import { tool } from "ai";
import { setCourseTimetableDataSchema } from "./aitm.schema.ts";
import { setCourseTimetable, SetCourseTimetableData } from "..";

export default tool({
  description: `
  Set a course timetable
Creates and updates "timetable" events for a course.
Can automaticaly
generate a series of calendar events based on simple schedules
(e.g. "Monday and Wednesday at
2:00pm" )

Existing timetable events for the course and course sections
will be updated if they
still are part of the timetable.
Otherwise, they will be deleted.
    `,
  parameters: setCourseTimetableDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetCourseTimetableData, "url"> ) => {
    try {
      const { data } = await setCourseTimetable(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    