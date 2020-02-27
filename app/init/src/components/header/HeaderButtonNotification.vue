<template>
  <div v-if="show" class="dropdown">
    <!-- Notification button -->
    <button
      class="btn btn-secondary dropdown-toggle ml-1"
      id="notification"
      type="button"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
      v-on:click="getAllNotifications"
    >
      <span v-if="nbNotifications > 0" class="badge badge-pill badge-info">
        {{ nbNotifications }}
      </span>
      Notifications
    </button>

    <!-- Notification box -->
    <div id="dropdown-notification" class="dropdown-menu dropdown-menu-lg-right" aria-labelledby="notification">
      <!-- Notification menu -->
      <div class="notification-menu">
        <router-link v-bind:to="'/notifications'">
          See all notifications
        </router-link>
        <a v-if="nbNotifications > 0" class="badge badge-secondary float-right" v-on:click="markAllNotificationsAsRead">
          Mark all as read
        </a>
      </div>

      <!-- No notification -->
      <div v-if="nbNotifications == 0" class="dropdown-item notification-item" style="margin-bottom:10px;">
        There is no new notification.
      </div>

      <!-- Notification items -->
      <div v-for="notification in notifications" v-bind:key="notification.id">
        <router-link class="dropdown-item notification-item" to="/notifications">
          Status of <b>{{ formatNotification(notification) }}</b> set to
          <span class="badge badge-pill" v-bind:class="statusCssClass(notification.status)">
            {{ notification.status }}
          </span>
          <div class="text-muted">
            <small>{{ notification.createdDate }}</small>
          </div>
        </router-link>
        <div class="dropdown-divider notification-divider"></div>
      </div>
    </div>
  </div>
</template>

<script>
import Mixins from "../utils/Mixins.vue";

export default {
  mixins: [Mixins],
  data: function() {
    return {
      notifications: [],
      nbNotifications: null,
      currentPage: {
        pageNum: 1,
        offset: 0,
        nbItems: 10
      }
    };
  },
  computed: {
    show() {
      let roles = ["standard", "advanced", "admin"];
      return roles.includes(this.$store.state.currentUser.role);
    }
  },
  methods: {
    formatNotification(notification) {
      if (notification.batchId) {
        let batchId = notification.batchId;
        let batchStatus = notification.status;
        return `batch Id ${batchId}`;
      } else if (notification.dataSourceId) {
        let dataSourceName = notification.dataSourceByDataSourceId.name;
        let dataSourceConnectivityStatus = notification.status;
        return `data source ${dataSourceName}`;
      }
    },
    getAllNotifications(page) {
      let payload = {
        query: this.$store.state.queryGetAllNotifications,
        variables: {
          first: page.nbItems,
          offset: page.offset,
          orderBy: ["CREATED_DATE_DESC"]
        }
      };
      let headers = {};
      if (this.$session.exists()) {
        headers = { Authorization: "Bearer " + this.$session.get("jwt") };
      }
      this.$http.post(this.$store.state.graphqlUrl, payload, { headers }).then(
        function(response) {
          if (response.data.errors) {
            this.displayError(response);
          } else {
            this.notifications = response.data.data.allNotifications.nodes;
            this.nbNotifications = response.data.data.allNotifications.totalCount;

            // Set current page
            this.currentPage = {
              pageNum: page.pageNum,
              offset: page.offset,
              nbItems: page.nbItems
            };
          }
        },
        // Error callback
        function(response) {
          this.displayError(response);
        }
      );
    },
    markAllNotificationsAsRead() {
      let payload = {
        query: this.$store.state.mutationMarkAllNotificationsAsRead
      };
      let headers = {};
      if (this.$session.exists()) {
        headers = { Authorization: "Bearer " + this.$session.get("jwt") };
      }
      this.$http.post(this.$store.state.graphqlUrl, payload, { headers }).then(
        function(response) {
          if (response.data.errors) {
            this.displayError(response);
          } else {
            // Force refresh list of notifications
            this.getAllNotifications(this.currentPage);
          }
        },
        // Error callback
        function(response) {
          this.displayError(response);
        }
      );
    }
  },
  created: function() {
    // Get notifications
    this.getAllNotifications(this.currentPage);

    // Capture notification via websocket listener
    this.$options.sockets.onmessage = function(data) {
      let message = JSON.parse(data.data);
      if (message.id == "notification" && message.type == "data") {
        this.nbNotifications = this.nbNotifications + 1;
        this.notifications.unshift(message.payload.data.listen.relatedNode); // Push notification to array
      }
    };
  }
};
</script>

<style>
#dropdown-notification {
  background: #2c3034;
  color: #ffffff;
  padding: 0;
  min-width: 300px;
  max-height: 450px;
  overflow: auto;
}
#dropdown-notification .notification-menu {
  padding: 10px 20px;
  background: #212529;
  margin-bottom: 10px;
}
#dropdown-notification .notification-item {
  font-size: 14px;
}
#dropdown-notification .notification-item {
  color: #ffffff;
}
#dropdown-notification .notification-item:hover {
  color: #ffffff;
  background: #323539;
}
#dropdown-notification .notification-divider {
  border-top: 1px solid #343a40;
}
</style>